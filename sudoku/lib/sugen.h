#include <stdint.h>
#include <stdbool.h>

/**
 * Attempts to generate a puzzle of the desired difficulty within the given number of iterations.
 * Returns 0 on success, or a negative error code if something goes wrong.
 * puzzle should be big enough to accept 81 integers. The actual difficulty will
 * be placed in diff.
 */
void db_generate_puzzle(uint8_t* puzzle, uint32_t* difficultyp, uint32_t difficulty, int32_t max_difficulty, uint32_t iterations, bool sofa);


int32_t db_solve_puzzle(const uint8_t* puzzle, uint8_t* solution, uint32_t* difficultyp, bool sofa);
