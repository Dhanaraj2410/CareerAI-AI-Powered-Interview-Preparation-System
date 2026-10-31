"""
CareerAI Coding Practice Seed Questions
---------------------------------------
Seeds foundational and advanced coding challenges across Python, SQL, and DSA.
"""

import json
from .models import CodingQuestion

SAMPLE_CODING_CHALLENGES = [
    {
        "title": "Two Sum - Hash Map Optimization",
        "slug": "two-sum",
        "category": "dsa",
        "difficulty": "easy",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nOptimal Time Complexity: O(n), Space Complexity: O(n).",
        "sample_input": "nums = [2, 7, 11, 15], target = 9",
        "sample_output": "[0, 1]",
        "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    hashmap = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in hashmap:\n            return [hashmap[diff], i]\n        hashmap[num] = i\n    return []\n",
        "solution_code": "def two_sum(nums, target):\n    hashmap = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in hashmap:\n            return [hashmap[diff], i]\n        hashmap[num] = i\n    return []",
        "explanation": "We use a single-pass hash map to store elements seen so far along with their indices. For each element, we check if the complement (target - num) exists in the map in O(1) time.",
        "test_cases_json": json.dumps([
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]}
        ])
    },
    {
        "title": "Reverse a Linked List",
        "slug": "reverse-linked-list",
        "category": "dsa",
        "difficulty": "easy",
        "description": "Given the `head` of a singly linked list represented as a Python list, reverse the list and return the reversed list.\n\nExample:\nInput: [1, 2, 3, 4, 5]\nOutput: [5, 4, 3, 2, 1]",
        "sample_input": "[1, 2, 3, 4, 5]",
        "sample_output": "[5, 4, 3, 2, 1]",
        "starter_code": "def reverse_list(items):\n    # Return reversed list\n    return items[::-1]\n",
        "solution_code": "def reverse_list(items):\n    prev = None\n    curr = items\n    return list(reversed(items))",
        "explanation": "In an in-place linked list pointer reversal, we maintain `prev`, `curr`, and `next_node` pointers. In Python array representation, the elements are reversed in O(n) time.",
        "test_cases_json": json.dumps([
            {"input": {"items": [1, 2, 3, 4, 5]}, "expected": [5, 4, 3, 2, 1]},
            {"input": {"items": [1, 2]}, "expected": [2, 1]},
            {"input": {"items": []}, "expected": []}
        ])
    },
    {
        "title": "Valid Anagram - Frequency Count",
        "slug": "valid-anagram",
        "category": "python",
        "difficulty": "easy",
        "description": "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
        "sample_input": "s = 'anagram', t = 'nagaram'",
        "sample_output": "True",
        "starter_code": "def is_anagram(s, t):\n    # Write your solution here\n    if len(s) != len(t):\n        return False\n    from collections import Counter\n    return Counter(s) == Counter(t)\n",
        "solution_code": "def is_anagram(s, t):\n    if len(s) != len(t):\n        return False\n    count = {}\n    for char in s:\n        count[char] = count.get(char, 0) + 1\n    for char in t:\n        if char not in count or count[char] == 0:\n            return False\n        count[char] -= 1\n    return True",
        "explanation": "Use a character frequency hash table or `collections.Counter`. If lengths differ or character frequencies do not match exactly, return False in O(n) time.",
        "test_cases_json": json.dumps([
            {"input": {"s": "anagram", "t": "nagaram"}, "expected": True},
            {"input": {"s": "rat", "t": "car"}, "expected": False},
            {"input": {"s": "listen", "t": "silent"}, "expected": True}
        ])
    },
    {
        "title": "Flatten Nested Dictionary",
        "slug": "flatten-nested-dictionary",
        "category": "python",
        "difficulty": "medium",
        "description": "Write a Python function `flatten_dict(d, parent_key='', sep='.')` that flattens an arbitrarily nested dictionary into a single-level dictionary where keys are joined by the separator.",
        "sample_input": "{'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}",
        "sample_output": "{'a': 1, 'b.c': 2, 'b.d.e': 3}",
        "starter_code": "def flatten_dict(d, parent_key='', sep='.'):\n    items = []\n    for k, v in d.items():\n        new_key = f\"{parent_key}{sep}{k}\" if parent_key else k\n        if isinstance(v, dict):\n            items.extend(flatten_dict(v, new_key, sep=sep).items())\n        else:\n            items.append((new_key, v))\n    return dict(items)\n",
        "solution_code": "def flatten_dict(d, parent_key='', sep='.'):\n    items = []\n    for k, v in d.items():\n        new_key = f\"{parent_key}{sep}{k}\" if parent_key else k\n        if isinstance(v, dict):\n            items.extend(flatten_dict(v, new_key, sep=sep).items())\n        else:\n            items.append((new_key, v))\n    return dict(items)",
        "explanation": "Recursively traverse the dictionary. If the value is another dictionary, recurse passing the composite key; otherwise append the key-value pair to the result list.",
        "test_cases_json": json.dumps([
            {"input": {"d": {"a": 1, "b": {"c": 2}}}, "expected": {"a": 1, "b.c": 2}},
            {"input": {"d": {"user": {"profile": {"name": "Alex"}}}}, "expected": {"user.profile.name": "Alex"}}
        ])
    },
    {
        "title": "SQL: Second Highest Salary",
        "slug": "sql-second-highest-salary",
        "category": "sql",
        "difficulty": "medium",
        "description": "Write a SQL query to find the second highest distinct salary from the `Employee` table. If there is no second highest salary, query should return NULL.\n\nTable: Employee (id INT, salary INT)",
        "sample_input": "SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1;",
        "sample_output": "SecondHighestSalary",
        "starter_code": "-- Write your SQL query below\nSELECT MAX(salary) AS SecondHighestSalary \nFROM Employee \nWHERE salary < (SELECT MAX(salary) FROM Employee);\n",
        "solution_code": "SELECT (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1) AS SecondHighestSalary;",
        "explanation": "Subquery with `ORDER BY salary DESC LIMIT 1 OFFSET 1` handles distinct ranking, and wrapping in an outer SELECT ensures a NULL return if fewer than 2 distinct salaries exist.",
        "test_cases_json": json.dumps([
            {"input": {"query_type": "salary_check"}, "expected": "PASS"}
        ])
    },
    {
        "title": "SQL: Department Top Three Salaries (Dense Rank)",
        "slug": "sql-department-top-three-salaries",
        "category": "sql",
        "difficulty": "hard",
        "description": "Write a SQL query to find employees who earn the top three unique salaries in each department using window functions (`DENSE_RANK()`).\n\nTables:\n- Employee (id, name, salary, departmentId)\n- Department (id, name)",
        "sample_input": "DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC)",
        "sample_output": "Department, Employee, Salary",
        "starter_code": "WITH RankedSalaries AS (\n    SELECT \n        d.name AS Department,\n        e.name AS Employee,\n        e.salary AS Salary,\n        DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) as rnk\n    FROM Employee e\n    JOIN Department d ON e.departmentId = d.id\n)\nSELECT Department, Employee, Salary\nFROM RankedSalaries\nWHERE rnk <= 3;\n",
        "solution_code": "WITH RankedSalaries AS (\n    SELECT \n        d.name AS Department,\n        e.name AS Employee,\n        e.salary AS Salary,\n        DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) as rnk\n    FROM Employee e\n    JOIN Department d ON e.departmentId = d.id\n)\nSELECT Department, Employee, Salary\nFROM RankedSalaries\nWHERE rnk <= 3;",
        "explanation": "Using `DENSE_RANK()` partitioned by `departmentId` ensures ties do not skip subsequent rank numbers (e.g. ranks 1, 1, 2, 3 are included).",
        "test_cases_json": json.dumps([
            {"input": {"query_type": "window_function_check"}, "expected": "PASS"}
        ])
    }
]

def seed_coding_questions():
    """Seeds baseline coding challenges if not already populated."""
    count = 0
    for data in SAMPLE_CODING_CHALLENGES:
        obj, created = CodingQuestion.objects.get_or_create(
            slug=data['slug'],
            defaults=data
        )
        if created:
            count += 1
    return count

