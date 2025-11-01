/home/webbp/github/AsciiDoctorArtisan/scripts/score_all_docs.py:85: DeprecationWarning: The 'avg_sentence_length' method has been deprecated due to being the same as 'words_per_sentence'. This method will be removed in thefuture.
  "avg_sentence_length": textstat.avg_sentence_length(clean_text),
🔍 Finding markdown files...
Found 37 markdown files

====================================================================================================
DOCUMENTATION READABILITY REPORT
====================================================================================================
Target: Grade 5.0 or below (Elementary School Reading Level)
Analyzed: 37 files

----------------------------------------------------------------------------------------------------
FILE                                                         GRADE    EASE     STATUS              
----------------------------------------------------------------------------------------------------
.github/copilot-instructions.md                              12.1     28.0     ❌ NEEDS WORK
CLAUDE.md                                                    13.6     24.4     ❌ NEEDS WORK
README.md                                                    6.8      70.6     ✓ GOOD
ROADMAP.md                                                   10.6     36.9     ⚠ FAIR
SECURITY.md                                                  4.4      80.0     ✅ EXCELLENT
docs/P0_TEST_FIXES_SUMMARY.md                                17.4     23.6     ❌ NEEDS WORK
docs/READABILITY_REPORT_20251031.md                          N/A      N/A      ⚠ Too short (< 100 words)
docs/README.md                                               17.5     -16.8    ❌ NEEDS WORK
docs/TEST_FIXES_QUICK_REF.md                                 14.6     33.1     ❌ NEEDS WORK
docs/architecture/ARCHITECTURAL_ANALYSIS_2025.md             11.7     28.1     ⚠ FAIR
docs/architecture/IMPLEMENTATION_REFERENCE.md                14.6     17.4     ❌ NEEDS WORK
docs/architecture/SPECIFICATIONS.md                          4.5      77.7     ✅ EXCELLENT
docs/developer/CONFIGURATION.md                              14.9     21.2     ❌ NEEDS WORK
docs/developer/PERFORMANCE_PROFILING.md                      17.3     14.7     ❌ NEEDS WORK
docs/developer/TEST_COVERAGE_SUMMARY.md                      14.6     20.1     ❌ NEEDS WORK
docs/developer/how-to-contribute.md                          3.1      87.4     ✅ EXCELLENT
docs/operations/SECURITY_AUDIT_GUIDE.md                      14.6     26.4     ❌ NEEDS WORK
docs/operations/SECURITY_AUDIT_IMPLEMENTATION.md             12.7     29.6     ❌ NEEDS WORK
docs/planning/IMPLEMENTATION_PLAN_v1.7.0.md                  17.7     22.4     ❌ NEEDS WORK
docs/planning/README.md                                      N/A      N/A      ⚠ Too short (< 100 words)
docs/planning/TASK_4_COMPLETION_SUMMARY.md                   16.4     15.8     ❌ NEEDS WORK
docs/qa/QA_EXECUTIVE_SUMMARY.md                              22.6     6.3      ❌ NEEDS WORK
docs/qa/QA_GRANDMASTER_AUDIT_2025.md                         16.3     22.8     ❌ NEEDS WORK
docs/qa/README.md                                            16.2     2.1      ❌ NEEDS WORK
docs/user/GITHUB_CLI_INTEGRATION.md                          10.8     41.4     ⚠ FAIR
docs/user/USER_TESTING_GUIDE.md                              7.1      66.0     ✓ GOOD
docs/user/how-to-use.md                                      2.3      95.6     ✅ EXCELLENT
openspec/README.md                                           3.0      92.6     ✅ EXCELLENT
openspec/changes/_template/design.md                         8.2      67.1     ⚠ FAIR
openspec/changes/_template/proposal.md                       5.0      76.9     ✓ GOOD
openspec/changes/_template/specs/example.md                  6.2      77.5     ✓ GOOD
openspec/changes/_template/tasks.md                          11.6     62.4     ⚠ FAIR
scripts/README.md                                            13.7     10.9     ❌ NEEDS WORK
templates/README.md                                          N/A      N/A      ⚠ Too short (< 100 words)
templates/default/images/README.md                           N/A      N/A      ⚠ Too short (< 100 words)
templates/default/themes/README.md                           N/A      N/A      ⚠ Too short (< 100 words)
tests/README.md                                              16.3     20.4     ❌ NEEDS WORK
----------------------------------------------------------------------------------------------------

====================================================================================================
SUMMARY STATISTICS
====================================================================================================
Average Grade Level: 11.82
Best Score: 2.27
Worst Score: 22.63

Distribution:
  ✅ EXCELLENT (≤5.0):     5 files (15.6%)
  ✓  GOOD (5.1-8.0):       4 files (12.5%)
  ⚠  FAIR (8.1-12.0):      5 files (15.6%)
  ❌ NEEDS WORK (>12.0):  18 files (56.2%)
  ⚠  ERRORS/SKIPPED:      5 files

====================================================================================================
FILES NEEDING IMPROVEMENT (Grade > 12.0)
====================================================================================================

📄 .github/copilot-instructions.md
   Grade: 12.1 | Words: 288 | Avg Sentence: 11.2 words

📄 docs/operations/SECURITY_AUDIT_IMPLEMENTATION.md
   Grade: 12.7 | Words: 536 | Avg Sentence: 14.5 words

📄 CLAUDE.md
   Grade: 13.6 | Words: 1609 | Avg Sentence: 15.2 words

📄 scripts/README.md
   Grade: 13.7 | Words: 215 | Avg Sentence: 8.1 words

📄 docs/architecture/IMPLEMENTATION_REFERENCE.md
   Grade: 14.6 | Words: 574 | Avg Sentence: 15.0 words

📄 docs/operations/SECURITY_AUDIT_GUIDE.md
   Grade: 14.6 | Words: 642 | Avg Sentence: 20.2 words

📄 docs/TEST_FIXES_QUICK_REF.md
   Grade: 14.6 | Words: 547 | Avg Sentence: 24.1 words

📄 docs/developer/TEST_COVERAGE_SUMMARY.md
   Grade: 14.6 | Words: 931 | Avg Sentence: 16.8 words

📄 docs/developer/CONFIGURATION.md
   Grade: 14.9 | Words: 666 | Avg Sentence: 18.4 words

📄 docs/qa/README.md
   Grade: 16.2 | Words: 156 | Avg Sentence: 12.8 words

📄 tests/README.md
   Grade: 16.3 | Words: 158 | Avg Sentence: 23.5 words

📄 docs/qa/QA_GRANDMASTER_AUDIT_2025.md
   Grade: 16.3 | Words: 2773 | Avg Sentence: 25.1 words

📄 docs/planning/TASK_4_COMPLETION_SUMMARY.md
   Grade: 16.4 | Words: 994 | Avg Sentence: 21.4 words

📄 docs/developer/PERFORMANCE_PROFILING.md
   Grade: 17.3 | Words: 468 | Avg Sentence: 24.3 words

📄 docs/P0_TEST_FIXES_SUMMARY.md
   Grade: 17.4 | Words: 1331 | Avg Sentence: 29.9 words

📄 docs/README.md
   Grade: 17.5 | Words: 250 | Avg Sentence: 7.6 words

📄 docs/planning/IMPLEMENTATION_PLAN_v1.7.0.md
   Grade: 17.7 | Words: 2507 | Avg Sentence: 30.5 words

📄 docs/qa/QA_EXECUTIVE_SUMMARY.md
   Grade: 22.6 | Words: 1357 | Avg Sentence: 41.3 words

====================================================================================================
LEGEND:
  Grade Level: Flesch-Kincaid Grade Level (lower is better)
  Ease: Flesch Reading Ease Score (higher is better, 70+ is easy)
  Target: Grade 5.0 or below for all user-facing documentation
====================================================================================================

⚠️  WARNING: 18 files exceed Grade 12.0
