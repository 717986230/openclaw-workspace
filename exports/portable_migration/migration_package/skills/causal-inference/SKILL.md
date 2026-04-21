---
name: causal-inference
description: Causal inference system with Do-calculus, potential outcomes, instrumental variables, and propensity score methods.
triggers:
  - "causal inference"
  - "causal effect"
  - "do-calculus"
  - "potential outcomes"
  - "instrumental variable"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: numpy
  - library: typing
  - library: dataclasses
  - library: enum
capabilities:
  - ate_estimation
  - do_calculus
  - backdoor_adjustment
  - frontdoor_adjustment
  - propensity_score_matching
  - instrumental_variable_analysis
---

# Causal Inference Skill

This skill provides a causal inference system with multiple methods including Do-calculus, potential outcomes, instrumental variables, and propensity score methods.

## How It Works

1.  **ATE Estimation:** Estimates average treatment effects using various methods.
2.  **Do-Calculus:** Computes intervention effects using Do-calculus.
3.  **Backdoor Adjustment:** Adjusts for confounders using backdoor criterion.
4.  **Frontdoor Adjustment:** Adjusts for mediators using frontdoor criterion.
5.  **Propensity Score Matching:** Uses propensity scores for causal inference.
6.  **Instrumental Variable Analysis:** Uses instrumental variables for causal inference.

## Usage

### Basic Operations

**Estimate ATE (Potential Outcomes):**
```python
inference = CausalInference(method=CausalMethod.POTENTIAL_OUTCOMES)
effect = inference.estimate_ate(treatment, outcome, covariates)
```

**Estimate ATE (Propensity Score):**
```python
inference = CausalInference(method=CausalMethod.PROPENSITY_SCORE)
effect = inference.estimate_ate(treatment, outcome, covariates)
```

**Estimate ATE (Instrumental Variable):**
```python
inference = CausalInference(method=CausalMethod.INSTRUMENTAL_VARIABLE)
effect = inference.estimate_ate(treatment, outcome, covariates)
```

### Advanced Operations

**Do-Calculus:**
```python
effect = inference.do_calculus(intervention, target, graph)
```

**Backdoor Adjustment:**
```python
effect = inference.backdoor_adjustment(treatment, outcome, confounders, data)
```

**Frontdoor Adjustment:**
```python
effect = inference.frontdoor_adjustment(treatment, outcome, mediator, data)
```

## Examples

### Example 1: Estimating Causal Effects
**User:** "What is the causal effect of treatment X on outcome Y?"
**Agent:** [Estimates the average treatment effect using potential outcomes framework]

### Example 2: Do-Calculus Analysis
**User:** "Compute the intervention effect using Do-calculus."
**Agent:** [Computes the intervention effect using Do-calculus and d-separation]

### Example 3: Backdoor Adjustment
**User:** "Adjust for confounders using backdoor criterion."
**Agent:** [Performs backdoor adjustment to estimate causal effects]

## Key Features

- **Multiple Methods:** Supports potential outcomes, propensity scores, and instrumental variables.
- **Do-Calculus:** Implements Do-calculus for intervention effects.
- **Adjustment Methods:** Supports backdoor and frontdoor adjustment.
- **Statistical Inference:** Provides confidence intervals and p-values.
- **Assumption Tracking:** Tracks assumptions for each method.

## Dependencies

- **Python Libraries:** `numpy`, `typing`, `dataclasses`, `enum`

## Best Practices

- **Method Selection:** Choose the appropriate method based on your data and assumptions.
- **Assumption Checking:** Verify assumptions before interpreting results.
- **Confidence Intervals:** Always consider confidence intervals when interpreting effects.
- **Robustness Checks:** Perform robustness checks to validate results.
- **Domain Knowledge:** Incorporate domain knowledge into causal graph construction.

## Contributing

To extend this skill:
1.  Add new causal inference methods to the `CausalInference` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
