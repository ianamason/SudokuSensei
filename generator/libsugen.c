/* Sudoku puzzle generator
 * Copyright (C) 2011 Daniel Beer <dlbeer@gmail.com>
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <ctype.h>
#include <string.h>
#include <time.h>
#include <getopt.h>

#include "sugen.h"

#ifndef ORDER
#define ORDER       3
#endif

#define DIM     (ORDER * ORDER)
#define ELEMENTS    (DIM * DIM)

/************************************************************************
 * Cell freedom analysis.
 *
 * Cell freedoms are sets, represented by bitfields. If bit N (counting
 * with LSB = 0) is set, then value (N+1) is present in the set.
 *
 * A cell freedom analysis results in a grid of sets, giving the immediately
 * allowable values in each cell position.
 *
 * If possible, it's cheaper to generate a freedom map for a new position by
 * modifying the previous position's freedom map, rather than rebuilding
 * from scratch.
 *
 * The search_least_free() function searches for the empty cell with the
 * smallest number of candidate values. It returns -1 if no empty cell was
 * found -- meaning that the grid is already solved.
 *
 * If the freedom for an empty cell is 0, this indicates that the grid is
 * unsolvable.
 */

typedef uint16_t set_t;

#define SINGLETON(v) (1 << ((v) - 1))
#define ALL_VALUES ((1 << DIM) - 1)

static uint32_t count_bits(int x)
{
  uint32_t count = 0;

  while (x) {
    x &= x - 1;
    count++;
  }

  return count;
}

static void freedom_eliminate(set_t *freedom, int x, int y, int v)
{
  set_t mask = ~SINGLETON(v);
  int b;
  uint32_t i, j;
  set_t saved = freedom[y * DIM + x];

  b = x;
  for (i = 0; i < DIM; i++) {
    freedom[b] &= mask;
    b += DIM;
  }

  b = y * DIM;
  for (i = 0; i < DIM; i++)
    freedom[b + i] &= mask;

  b = (y - y % ORDER) * DIM + x - x % ORDER;
  for (i = 0; i < ORDER; i++) {
    for (j = 0; j < ORDER; j++)
      freedom[b + j] &= mask;

    b += DIM;
  }

  freedom[y * DIM + x] = saved;
}

static void init_freedom(const uint8_t *problem, set_t *freedom)
{
  uint32_t x, y;

  for (x = 0; x < ELEMENTS; x++)
    freedom[x] = ALL_VALUES;

  for (y = 0; y < DIM; y++)
    for (x = 0; x < DIM; x++) {
      uint8_t v = problem[y * DIM + x];

      if (v)
        freedom_eliminate(freedom, x, y, v);
    }
}

static uint32_t sanity_check(const uint8_t *problem, const set_t *freedom)
{
  uint32_t i;

  for (i = 0; i < ELEMENTS; i++) {
    uint8_t v = problem[i];

    if (v) {
      set_t f = freedom[i];

      if (!(f & SINGLETON(v)))
        return -1;
    }
  }

  return 0;
}

static int32_t search_least_free(const uint8_t *problem, const set_t *freedom)
{
  uint32_t i;
  int32_t best_index = -1;
  int32_t best_score = -1;

  for (i = 0; i < ELEMENTS; i++) {
    uint8_t v = problem[i];

    if (!v) {
      uint32_t score = count_bits(freedom[i]);

      if (best_score < 0 || score < best_score) {
        best_index = i;
        best_score = score;
      }
    }
  }

  return best_index;
}

/************************************************************************
 * Set-oriented freedom analysis.
 *
 * In normal freedom analysis, we find candidate values for each cell. In
 * set-oriented freedom analysis, we find candidate cells for each value.
 * There are 3 * DIM sets to consider (DIM boxes, rows and columns).
 *
 * The sofa() function returns the size of the smallest set of positions
 * found, along with a list of those positions and a value which can occupy
 * all of those positions. It returns -1 if a set of positions couldn't
 * be found.
 *
 * If it returns 0, this indicates that there exists a set, missing a value,
 * with no possible positions for that value -- the grid is therefore
 * unsolvable.
 *
 * If the program is compiled with -DNO_SOFA, this analysis is not used.
 */

struct sofa_context {
  const uint8_t     *grid;
  const set_t       *freedom;

  int32_t       best[DIM];
  int32_t       best_size;
  int32_t       best_value;
};

static void sofa_set(struct sofa_context *ctx, const int32_t *set)
{
  int32_t count[DIM];
  int32_t i;
  int32_t best = -1;
  set_t missing = ALL_VALUES;

  /* Find out what's missing from the set, and how many available
   * slots for each missing number.
   */
  memset(count, 0, sizeof(count));
  for (i = 0; i < DIM; i++) {
    uint8_t v = ctx->grid[set[i]];

    if (v) {
      missing &= ~SINGLETON(v);
    } else {
      set_t freedom = ctx->freedom[set[i]];
      int32_t j;

      for (j = 0; j < DIM; j++)
        if (freedom & (1 << j))
          count[j]++;
    }
  }

  /* Look for the missing number with the fewest available slots. */
  for (i = 0; i < DIM; i++)
    if ((missing & (1 << i)) &&
        (best < 0 || count[i] < count[best]))
      best = i;

  /* Did we find anything? */
  if (best < 0)
    return;

  /* If it's better than anything we've found so far, save the result */
  if (ctx->best_size < 0 || count[best] < ctx->best_size) {
    int32_t j = 0;
    set_t mask = 1 << best;

    ctx->best_value = best + 1;
    ctx->best_size = count[best];

    for (i = 0; i < DIM; i++)
      if (!ctx->grid[set[i]] &&
          (ctx->freedom[set[i]] & mask))
        ctx->best[j++] = set[i];
  }
}

static int32_t sofa(const uint8_t *grid, const set_t *freedom, int32_t *set, int32_t *value)
{
  struct sofa_context ctx;
  int32_t i;

  memset(&ctx, 0, sizeof(ctx));
  ctx.grid = grid;
  ctx.freedom = freedom;
  ctx.best_size = -1;
  ctx.best_value = -1;

  for (i = 0; i < DIM; i++) {
    int32_t b = (i / ORDER) * ORDER * DIM + (i % ORDER) * ORDER;
    int32_t set[DIM];
    int32_t j;

    for (j = 0; j < DIM; j++)
      set[j] = j * DIM + i;
    sofa_set(&ctx, set);

    for (j = 0; j < DIM; j++)
      set[j] = i * DIM + j;
    sofa_set(&ctx, set);

    for (j = 0; j < DIM; j++)
      set[j] = b + (j / ORDER) * DIM + j % ORDER;
    sofa_set(&ctx, set);
  }

  memcpy(set, ctx.best, sizeof(ctx.best));
  *value = ctx.best_value;
  return ctx.best_size;
}

/************************************************************************
 * Solver
 *
 * The solver works using recursive backtracking. The general idea is to
 * find the cell with the smallest possible number of candidate values, and
 * to try each candidate, recursively solving until we find a solution.
 *
 * However, in cases where a cell has multiple candidates, we also consider
 * set-oriented backtracking -- choosing a value and trying each candidate
 * position. If this yields a smaller branching factor (it often eliminates
 * the need for backtracking), we try it instead.
 *
 * We keep searching until we've either found two solutions (demonstrating
 * that the grid does not have a unique solution), or we exhaust the search
 * tree.
 *
 * We also calculate a branch-difficulty score:
 *
 *    Sigma [(B_i - 1) ** 2]
 *
 * Where B_i are the branching factors at each node in the search tree
 * following the path from the root to the solution. A puzzle that could
 * be solved without backtracking has a branch-difficulty of 0.
 *
 * The final difficulty is:
 *
 *    Difficulty = B * C + E
 *
 * Where B is the branch-difficulty, E is the number of empty cells, and C
 * is the first power of ten greater than the number of elements.
 */

struct solve_context {
  uint8_t  problem[ELEMENTS];
  uint32_t count;
  uint8_t  *solution;
  uint32_t branch_score;
};

static void solve_recurse_no_sofa(struct solve_context *ctx, const set_t *freedom, uint32_t diff)
{
  set_t new_free[ELEMENTS];
  set_t mask;
  int32_t r;
  uint32_t i;
  uint32_t bf;

  r = search_least_free(ctx->problem, freedom);
  if (r < 0) {
    if (!ctx->count) {
      ctx->branch_score = diff;
      if (ctx->solution)
        memcpy(ctx->solution, ctx->problem, ELEMENTS * sizeof(ctx->solution[0]));
    }

    ctx->count++;
    return;
  }

  mask = freedom[r];

  bf = count_bits(mask) - 1;
  diff += bf * bf;

  for (i = 0; i < DIM; i++)
    if (mask & (1 << i)) {
      memcpy(new_free, freedom, sizeof(new_free));
      freedom_eliminate(new_free, r % DIM, r / DIM, i + 1);
      ctx->problem[r] = i + 1;
      solve_recurse_no_sofa(ctx, new_free, diff);

      if (ctx->count >= 2)
        return;
    }

  ctx->problem[r] = 0;
}

static void solve_recurse_sofa(struct solve_context *ctx, const set_t *freedom, uint32_t diff)
{
  set_t new_free[ELEMENTS];
  set_t mask;
  int32_t r;
  uint32_t i;
  uint32_t bf;

  r = search_least_free(ctx->problem, freedom);
  if (r < 0) {
    if (!ctx->count) {
      ctx->branch_score = diff;
      if (ctx->solution)
        memcpy(ctx->solution, ctx->problem, ELEMENTS * sizeof(ctx->solution[0]));
    }

    ctx->count++;
    return;
  }

  mask = freedom[r];

  /* If we can't determine a cell value, see if set-oriented
   * backtracking provides a smaller branching factor.
   */
  if (mask & (mask - 1)) {
    int32_t set[DIM];
    int32_t value;
    int32_t size;

    size = sofa(ctx->problem, freedom, set, &value);
    //iam: sofa set is smaller than |freedom[r]| ?
    if (size >= 0 && size < count_bits(mask)) {
      bf = size - 1;
      diff += bf * bf;

      for (i = 0; i < size; i++) {
        int s = set[i];

        memcpy(new_free, freedom, sizeof(new_free));
        freedom_eliminate(new_free, s % DIM, s / DIM, value);
        ctx->problem[s] = value;
        solve_recurse_sofa(ctx, new_free, diff);
        ctx->problem[s] = 0;

        if (ctx->count >= 2)
          return;
      }

      return;
    }
  }

  /* Otherwise, fall back to cell-oriented backtracking. */
  bf = count_bits(mask) - 1;
  diff += bf * bf;

  for (i = 0; i < DIM; i++)
    if (mask & (1 << i)) {
      memcpy(new_free, freedom, sizeof(new_free));
      freedom_eliminate(new_free, r % DIM, r / DIM, i + 1);
      ctx->problem[r] = i + 1;
      solve_recurse_sofa(ctx, new_free, diff);

      if (ctx->count >= 2)
        return;
    }

  ctx->problem[r] = 0;
}



static int32_t solve(const uint8_t *problem, uint8_t *solution, uint32_t *diff, bool sofa)
{
  struct solve_context ctx;
  set_t freedom[ELEMENTS];

  memcpy(ctx.problem, problem, sizeof(ctx.problem));
  ctx.count = 0;
  ctx.branch_score = 0;
  ctx.solution = solution;

  init_freedom(problem, freedom);
  if (sanity_check(problem, freedom) < 0)
    return -1;

  if (sofa) {
    solve_recurse_sofa(&ctx, freedom, 0);
  } else {
    solve_recurse_no_sofa(&ctx, freedom, 0);
  }

  /* Calculate a difficulty score */
  if (diff) {
    uint32_t empty = 0;
    uint32_t mult = 1;
    uint32_t i;

    for (i = 0; i < ELEMENTS; i++)
      if (!problem[i])
        empty++;

    while (mult <= ELEMENTS)
      mult *= 10;

    *diff = ctx.branch_score * mult + empty;

    printf("solver (sofa=%d) returns %d diff %d empty %d\n", sofa, ctx.count - 1, diff ? *diff : 0, empty);

  }

  return ctx.count - 1;
}

/************************************************************************
 * Grid generator
 *
 * We generate grids using a backtracking algorithm similar to the basic
 * solver algorithm. At each step, choose a cell with the smallest number
 * of possible values, and try each value, solving recursively. The key
 * difference is that the values are tested in a random order.
 *
 * An empty grid can be initially populated with a large number of values
 * without backtracking. In the ORDER == 3 case, we can easily fill the
 * whole top band the the first column before resorting to backtracking.
 */

static int pick_value(set_t set)
{
  int x = random() % count_bits(set);
  int i;

  for (i = 0; i < DIM; i++)
    if (set & (1 << i)) {
      if (!x)
        return i + 1;
      x--;
    }

  return 0;
}

static void choose_b1(uint8_t *problem)
{
  set_t set = ALL_VALUES;
  int i, j;

  for (i = 0; i < ORDER; i++)
    for (j = 0; j < ORDER; j++) {
      int v = pick_value(set);

      problem[i * DIM + j] = v;
      set &= ~SINGLETON(v);
    }
}

#if ORDER == 3
static void choose_b2(uint8_t *problem)
{
  set_t used[ORDER];
  set_t chosen[ORDER];
  set_t set_x, set_y;
  int i, j;

  memset(used, 0, sizeof(used));
  memset(chosen, 0, sizeof(chosen));

  /* Gather used values from B1 by box-row */
  for (i = 0; i < ORDER; i++)
    for (j = 0; j < ORDER; j++)
      used[i] |= SINGLETON(problem[i * DIM + j]);

  /* Choose the top box-row for B2 */
  set_x = used[1] | used[2];
  for (i = 0; i < ORDER; i++) {
    int v = pick_value(set_x);
    set_t mask = SINGLETON(v);

    chosen[0] |= mask;
    set_x &= ~mask;
  }

  /* Choose values for the middle box-row, as long as we can */
  set_x = (used[0] | used[2]) & ~chosen[0];
  set_y = (used[0] | used[1]) & ~chosen[0];

  while (count_bits(set_y) > 3) {
    int v = pick_value(set_x);
    set_t mask = SINGLETON(v);

    chosen[1] |= mask;
    set_x &= ~mask;
    set_y &= ~mask;
  }

  /* We have no choice for the remainder */
  chosen[1] |= set_x & ~set_y;
  chosen[2] |= set_y;

  /* Permute the triplets in each box-row */
  for (i = 0; i < ORDER; i++) {
    set_t set = chosen[i];
    int j;

    for (j = 0; j < ORDER; j++) {
      int v = pick_value(set);

      problem[i * DIM + j + ORDER] = v;
      set &= ~SINGLETON(v);
    }
  }
}

static void choose_b3(uint8_t *problem)
{
  int i;

  for (i = 0; i < ORDER; i++) {
    set_t set = ALL_VALUES;
    int j;

    /* Eliminate already-used values in this row */
    for (j = 0; j + ORDER < DIM; j++)
      set &= ~SINGLETON(problem[i * DIM + j]);

    /* Permute the remaining values in the last box-row */
    for (j = 0; j < ORDER; j++) {
      int v = pick_value(set);

      problem[i * DIM + DIM - ORDER + j] = v;
      set &= ~SINGLETON(v);
    }
  }
}
#endif /* ORDER == 3 */

static void choose_col1(uint8_t *problem)
{
  set_t set = ALL_VALUES;
  int i;

  for (i = 0; i < ORDER; i++)
    set &= ~SINGLETON(problem[i * DIM]);

  for (; i < DIM; i++) {
    int v = pick_value(set);

    problem[i * DIM] = v;
    set &= ~SINGLETON(v);
  }
}

static int choose_rest(uint8_t *grid, const set_t *freedom)
{
  int i = search_least_free(grid, freedom);
  set_t set;

  if (i < 0)
    return 0;

  set = freedom[i];
  while (set) {
    set_t new_free[ELEMENTS];
    int v = pick_value(set);

    set &= ~SINGLETON(v);
    grid[i] = v;

    memcpy(new_free, freedom, sizeof(new_free));
    freedom_eliminate(new_free, i % DIM, i / DIM, v);

    if (!choose_rest(grid, new_free))
      return 0;
  }

  grid[i] = 0;
  return -1;
}

static void choose_grid(uint8_t *grid)
{
  set_t freedom[ELEMENTS];

  memset(grid, 0, sizeof(grid[0]) * ELEMENTS);

  choose_b1(grid);
#if ORDER == 3
  choose_b2(grid);
  choose_b3(grid);
#endif
  choose_col1(grid);

  init_freedom(grid, freedom);
  choose_rest(grid, freedom);
}

/************************************************************************
 * Puzzle generator
 *
 * To generate a puzzle, we start with a solution grid, and an initial
 * puzzle (which may be the same as the solution). We try altering the
 * puzzle by either randomly adding a pair of clues from the solution, or
 * randomly removing a pair of clues. After each alteration, we check to
 * see if we have a valid puzzle. If it is, and it's more difficult than
 * anything we've encountered so far, save it as the best puzzle.
 *
 * To avoid getting stuck in local minima in the space of puzzles, we allow
 * the algorithm to wander for a few steps before starting again from the
 * best-so-far puzzle.
 */

static int harden_puzzle(const uint8_t *solution, uint8_t *puzzle, int max_iter, int max_score, int target_score, bool sofa)
{
  uint32_t best = 0;
  int i;

  solve(puzzle, NULL, &best, sofa);

  for (i = 0; i < max_iter; i++) {
    uint8_t next[ELEMENTS];
    int j;

    printf("\tIteration: %d   %d\n", i, best);

    memcpy(next, puzzle, sizeof(next));

    for (j = 0; j < DIM * 2; j++) {
      int c = random() % ELEMENTS;
      uint32_t s;

      if (random() & 1) {
        next[c] = solution[c];
        next[ELEMENTS - c - 1] = solution[ELEMENTS - c - 1];
      } else {
        next[c] = 0;
        next[ELEMENTS - c - 1] = 0;
      }

      if (!solve(next, NULL, &s, sofa) &&
          s > best && (s <= max_score || max_score < 0)) {
        memcpy(puzzle, next, sizeof(puzzle[0]) * ELEMENTS);
        best = s;

        if (target_score >= 0 && s >= target_score) {
          printf("iteration: %d\n", i);
          return best;
        }
      }
    }
  }
  printf("iteration: %d\n", max_iter);
  return best;
}


/************************************************************************
 * API
 *
 */


int32_t db_solve_puzzle(const uint8_t* puzzle, uint8_t* solution, uint32_t* difficultyp, bool sofa){
  return solve(puzzle, solution, difficultyp, sofa);
}

void db_generate_puzzle(uint8_t* puzzle, uint32_t* difficultyp, uint32_t difficulty, int32_t max_difficulty, uint32_t iterations, bool sofa){
  uint8_t grid[ELEMENTS];
  srandom(time(NULL));
  choose_grid(grid);
  memcpy(puzzle, grid, ELEMENTS * sizeof(uint8_t));
  *difficultyp = harden_puzzle(grid, puzzle, iterations, max_difficulty, difficulty, sofa);
  return;
}
