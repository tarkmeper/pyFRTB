[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=coverage)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=tarkmeper_pyFRTB&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=tarkmeper_pyFRTB)

# pyFRTB

This is (in the current state) proof-of-concept for a Python implementation of the Fundamental Review of the Trading Book (FRTB) rules. The goal of
this library was to both be a fast parallel aggregator and to enable supporting multiple different rule-sets (example
changing between FRTB rule sets or country specific rules).

The system is designed around creating partial aggregations from sets of trades which can the be scaled and merged. Partial aggregations are safe to be serialized via Pickle and so can be executed in
parallel on portions of trade population and then merged in any combination.

## Todos

* __Lots and lots of testing.__ Some preliminary tests are included.
* Updates to rules. This is based on the first published standard (d352) and there have been changes in the rules more
  recently. Only the d352 rules were partially implemented, not updated for the d457 standard.
* Implementation of securitization and collateralized portfolios for JTD calculations

## Example

See the examples folder for a sample of input formats and how to combine and aggregate results.

## Testing

The idea in terms of the testing was to link tests cases to specific paragraphs in the Basel regulations. Exmaples can
be seen in the tests/d352 folder. The coverage of relevant paragraphs at the moment is very low, but is the best way to
ensure that all rules have been correctly captured. 