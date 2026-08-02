from pathlib import Path

import yaml


def load_yaml(file_path: Path) -> dict:
    """Load and return data from a YAML file."""
    with file_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data


if __name__ == "__main__":
    requirements_v1_path = Path("data/case_study/requirements_v1.yaml")
    requirements_v2_path = Path("data/case_study/requirements_v2.yaml")
    test_cases_path = Path("data/case_study/test_cases.yaml")
    test_results_path = Path("data/case_study/test_results.yaml")

    requirements_v1_data = load_yaml(requirements_v1_path)
    requirements_v2_data = load_yaml(requirements_v2_path)
    test_cases_data = load_yaml(test_cases_path)
    test_results_data = load_yaml(test_results_path)

    requirements_v1 = requirements_v1_data["requirements"]
    requirements_v2 = requirements_v2_data["requirements"]
    test_cases = test_cases_data["test_cases"]
    test_results = test_results_data["test_results"]

    print(f"Loaded {len(requirements_v1)} requirements from version 1.")
    print(f"Loaded {len(requirements_v2)} requirements from version 2.")
    print(f"Loaded {len(test_cases)} test cases.")
    print(f"Loaded {len(test_results)} test results.")

    

