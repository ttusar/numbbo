#include <assert.h>

#include "coco.h"
#include "coco_problem.c"

typedef struct {
  double factor;
} transform_obj_penalize_data_t;

static void transform_obj_penalize_evaluate(coco_problem_t *problem, const double *x, double *y) {
  transform_obj_penalize_data_t *data = coco_problem_transformed_get_data(problem);
  const double *lower_bounds = problem->smallest_values_of_interest;
  const double *upper_bounds = problem->largest_values_of_interest;
  double penalty = 0.0;
  size_t i;
  for (i = 0; i < problem->number_of_variables; ++i) {
    const double c1 = x[i] - upper_bounds[i];
    const double c2 = lower_bounds[i] - x[i];
    assert(lower_bounds[i] < upper_bounds[i]);
    if (c1 > 0.0) {
      penalty += c1 * c1;
    } else if (c2 > 0.0) {
      penalty += c2 * c2;
    }
  }
  assert(coco_problem_transformed_get_inner_problem(problem) != NULL);
  /*assert(problem->state != NULL);*/
  coco_evaluate_function(coco_problem_transformed_get_inner_problem(problem), x, y);
  for (i = 0; i < problem->number_of_objectives; ++i) {
    y[i] += data->factor * penalty;
  }
  assert(y[0] + 1e-13 >= self->best_value[0]);
}

/**
 * Add a penalty to all evaluations outside of the region of interest
 * of ${inner_problem}.
 */
static coco_problem_t *f_transform_obj_penalize(coco_problem_t *inner_problem, const double factor) {
  coco_problem_t *problem;
  transform_obj_penalize_data_t *data;
  assert(inner_problem != NULL);
  /* assert(offset != NULL); */

  data = coco_allocate_memory(sizeof(*data));
  data->factor = factor;
  problem = coco_problem_transformed_allocate(inner_problem, data, NULL);
  problem->evaluate_function = transform_obj_penalize_evaluate;
  /* No need to update the best value as the best parameter is feasible */
  return problem;
}
