-- 1. Ghost employees: missing critical information
SELECT 'Missing SSN' AS issue, employee_id, first_name, last_name
FROM employees
WHERE ssn IS NULL OR ssn = ''

UNION ALL

SELECT 'Missing Email', employee_id, first_name, last_name
FROM employees
WHERE email IS NULL OR email = ''

UNION ALL

SELECT 'Missing Department', employee_id, first_name, last_name
FROM employees
WHERE department_id IS NULL

UNION ALL

SELECT 'Zero Salary Active', employee_id, first_name, last_name
FROM employees
WHERE salary <= 0 AND is_active = 1;

-- 2. Duplicate SSNs (possible ghost employees)
SELECT ssn, COUNT(*) AS count
FROM employees
WHERE ssn IS NOT NULL
GROUP BY ssn
HAVING COUNT(*) > 1;

-- 3. Payroll calculation errors
SELECT p.payroll_id, p.employee_id,
       p.gross_pay, p.deductions, p.net_pay,
       (p.gross_pay - p.deductions) AS calculated_net
FROM payroll p
WHERE ABS(p.net_pay - (p.gross_pay - p.deductions)) > 0.01;

-- 4. Overtime hours without overtime pay
--    (requires joining with employees for salary rate)
SELECT p.payroll_id, p.employee_id, p.overtime_hours, p.gross_pay,
       e.salary/12 AS base_monthly
FROM payroll p
JOIN employees e ON p.employee_id = e.employee_id
WHERE p.overtime_hours > 0
  AND p.gross_pay <= e.salary/12;   -- gross not increased for overtime

-- 5. Negative deductions
SELECT payroll_id, employee_id, deductions
FROM payroll
WHERE deductions < 0;

-- 6. Gross pay zero or negative
SELECT payroll_id, employee_id, gross_pay
FROM payroll
WHERE gross_pay <= 0;