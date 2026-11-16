# Rust checkpoints

All 40 unique exercises in these four checkpoint lists have bundled test suites.
Repeated exercises use the same suite. Levels, difficulty and XP depend on the
checkpoint version; the tables below preserve the supplied groupings.

Run an exercise from your solution repository:

```sh
rt min_and_max
rt matrix_multiplication
rt rpn
```

Or run every supported exercise found in a checkpoint directory:

```sh
rt --all /path/to/checkpoint
```

Use `rt --list` to list all bundled suites. If you installed an older copy,
rerun `sh install.sh` from the updated tester directory.

## Checkpoint 1

| Level | Difficulty | XP per exercise | Exercises |
| --- | --- | --- | --- |
| 1 | 2 | 2.8k | `min_and_max`, `matrix_multiplication` |
| 2 | 4 | 5.6k | `reverse_it`, `smallest`, `modify_letter` |
| 3 | 6 | 8.4k | `counting_words`, `partial_sums`, `inv_pyramid` |
| 4 | 8 | 11.2k | `insertion_sort`, `rpn` |

## Checkpoint 2

| Level | Difficulty | XP per exercise | Exercises |
| --- | --- | --- | --- |
| 1 | 2 | 4.3k | `previousprime`, `nextprime`, `reverse_it` |
| 2 | 4 | 8.6k | `count_factorial_steps`, `lucas_number`, `own_and_return`, `matrix_determinant` |
| 3 | 6 | 12.9k | `check_user_name`, `get_document_id`, `dress_code` |
| 4 | 8 | 17.2k | `rot21`, `order_books`, `prime_checker` |
| 5 | 10 | 21.5k | `queens`, `scytale_decoder` |

## Checkpoint 3

| Level | Difficulty | XP per exercise | Exercises |
| --- | --- | --- | --- |
| 1 | 2 | 5.5k | `counting_words`, `partial_sums`, `inv_pyramid`, `previousprime`, `nextprime`, `reverse_it` |
| 2 | 4 | 11.0k | `check_user_name`, `get_document_id`, `dress_code` |
| 3 | 6 | 16.5k | `negative_spelling`, `rpn`, `queens`, `scytale_decoder` |
| 4 | 8 | 22.0k | `office_worker`, `matrix_display`, `organize_garage` |
| 5 | 10 | 27.5k | `moving_targets`, `format_me`, `blood_types_s` |
| 6 | 12 | 33.0k | `car_rental`, `drop_the_blog`, `lunch_queue` |

## Checkpoint 4

| Level | Difficulty | XP per exercise | Exercises |
| --- | --- | --- | --- |
| 1 | 2 | 7.6k | `min_and_max`, `count_factorial_steps`, `matrix_multiplication` |
| 2 | 4 | 15.2k | `reverse_it`, `counting_words`, `smallest`, `modify_letter` |
| 3 | 6 | 22.8k | `partial_sums`, `inv_pyramid`, `previousprime`, `nextprime`, `profanity_filter`, `prime_checker`, `scytale_decoder` |
| 4 | 8 | 30.4k | `insertion_sort`, `rpn`, `rot21`, `order_books`, `matrix_determinant` |
| 5 | 10 | 38.0k | `office_worker`, `blood_types_s` |
| 6 | 12 | 45.6k | `matrix_display`, `queens`, `lunch_queue` |
| 7 | 14 | 53.2k | `drop_the_blog`, `filter_table`, `display_table` |
| 8 | 16 | 60.8k | `flat_tree` |
| 9 | 18 | 68.4k | `brackets_matching`, `brain_fuck` |

The first supplied list starts with two exercises before its Level 2 heading;
they are shown as Level 1. The third list starts with six exercises before
Level 2; they are also shown as Level 1.

These are the bundled snapshot suites described in the
[coverage notes](README.md#coverage-and-provenance). Listing a suite confirms
that it is available, rather than guaranteeing a match with every platform
version. Some suites require external dependencies or a particular toolchain.
