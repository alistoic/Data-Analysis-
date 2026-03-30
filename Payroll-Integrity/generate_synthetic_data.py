import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# Setup
fake = Faker()
np.random.seed(42)
random.seed(42)

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# 1. DEPARTMENTS
departments = pd.DataFrame({
    'dept_id': [1, 2, 3, 4, 5],
    'dept_name': ['Sales', 'Engineering', 'HR', 'Finance', 'Operations']
})

# 2. EMPLOYEES (Clean Base)
n_employees = 500
employee_ids = list(range(1, n_employees + 1))

data = {
    'employee_id': employee_ids,
    'first_name': [fake.first_name() for _ in range(n_employees)],
    'last_name': [fake.last_name() for _ in range(n_employees)],
    'ssn': [fake.ssn() for _ in range(n_employees)],
    'email': [fake.email() for _ in range(n_employees)],
    'department_id': [random.choice(departments['dept_id']) for _ in range(n_employees)],
    'hire_date': [fake.date_between(start_date='-5y', end_date='today') for _ in range(n_employees)],
    'salary': np.random.normal(60000, 15000, n_employees).clip(30000, 150000).astype(int),
    'is_active': [True] * n_employees
}

employees = pd.DataFrame(data)

# 3. INJECT GHOST EMPLOYEE ANOMALIES (Modifying the Employee Master)
# ----------------------------------------------------------------
# A. Missing SSN
employees.loc[10, 'ssn'] = None

# B. Duplicate SSN (Creating a 'Ghost' clone of index 42)
ghost_clone = employees.iloc[42].copy()
ghost_clone['employee_id'] = n_employees + 1
ghost_clone['first_name'], ghost_clone['last_name'] = 'Ghost', 'Employee'
employees = pd.concat([employees, ghost_clone.to_frame().T], ignore_index=True)

# C. Missing critical contact info
employees.loc[200, 'email'] = None

# D. Salary = 0 anomaly
employees.loc[300, 'salary'] = 0

# E. Missing Department link (Foreign Key violation)
employees.loc[400, 'department_id'] = None

# 4. PAYROLL GENERATION
# ----------------------------------------------------------------
pay_period = (datetime.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
payroll_records = []

for _, emp in employees.iterrows():
    # Logic: Monthly base
    base_monthly = emp['salary'] / 12
    
    # Overtime logic (Poisson distribution for realism)
    overtime_hours = np.random.poisson(2) * 5 if random.random() > 0.7 else 0
    overtime_pay = overtime_hours * (base_monthly / 160) * 1.5
    
    gross = base_monthly + overtime_pay
    deductions = gross * (0.2 + np.random.uniform(-0.05, 0.05))
    net_pay = gross - deductions

    payroll_records.append({
        'payroll_id': len(payroll_records) + 1,
        'employee_id': emp['employee_id'],
        'pay_period': pay_period,
        'gross_pay': round(gross, 2),
        'deductions': round(deductions, 2),
        'net_pay': round(net_pay, 2),
        'overtime_hours': overtime_hours
    })

payroll = pd.DataFrame(payroll_records)

# 5. INJECT CALCULATION ERRORS (Modifying the Payroll Records)
# ----------------------------------------------------------------
# Error 1: Net pay math doesn't add up (Gross - Ded != Net)
payroll.loc[50, 'net_pay'] += 500.00

# Error 2: Missing Overtime Pay (Corrected reference to the employee's base salary)
error2_emp_id = payroll.loc[150, 'employee_id']
# Correctly pulling salary from the employees table to simulate the 'missing' pay
emp_base_salary = employees.loc[employees['employee_id'] == error2_emp_id, 'salary'].values[0]
payroll.loc[150, 'overtime_hours'] = 15
payroll.loc[150, 'gross_pay'] = round(emp_base_salary / 12, 2) 

# Error 3: Negative Deductions (System glitch)
payroll.loc[300, 'deductions'] = -150.75

# Error 4: Zero Paycheck for an Active Employee
payroll.loc[400, ['gross_pay', 'net_pay']] = 0.0

# 6. SAVE OUTPUT
# ----------------------------------------------------------------
employees.to_csv('data/employees.csv', index=False)
payroll.to_csv('data/payroll.csv', index=False)
departments.to_csv('data/departments.csv', index=False)

print(f"✅ Success! Generated {len(employees)} employees and {len(payroll)} payroll records.")
print("📁 Files saved to: /data/ (employees.csv, payroll.csv, departments.csv)")