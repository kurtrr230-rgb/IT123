# Week 3 Ubuntu Verification Results

Executed on the Ubuntu 26.04.1 LTS VM. The [raw guest test output](verification-output.txt) reports 12 PASS, 0 FAIL, and a shell exit code of 0. Password-backed login tests were performed separately.

| Test | Expected | Observed |
| --- | --- | --- |
| student2 is in labusers | Yes | PASS: `id student2` lists labusers |
| faculty2 is in facultygrp | Yes | PASS: `id faculty2` lists facultygrp |
| student4 is in studentgrp | Yes | PASS: `id student4` lists studentgrp |
| student2 reads /labdata/sample.txt at mode 770 | Allowed | PASS, exit 0 |
| student2 creates /labdata/student2-test.txt at mode 770 | Allowed | PASS, exit 0 |
| student2 reads /labdata/sample.txt at mode 750 | Allowed | PASS, exit 0 |
| student2 creates another file in /labdata at mode 750 | Denied | PASS, permission denied, exit 1 |
| faculty2 reads and creates a file in /facultydata | Allowed | PASS, both exit 0 |
| student4 reads /studentdata/sample.txt | Allowed | PASS, exit 0 |
| student4 creates a file in /studentdata | Denied | PASS, permission denied, exit 1 |
| student4 modifies existing sample.txt | Denied | PASS, permission denied, exit 2 |
| student4 accesses /facultydata | Denied | PASS, permission denied, exit 1 |
| faculty2 accesses /studentdata | Denied | PASS, permission denied, exit 1 |
| student2 accesses /facultydata and /studentdata | Denied | PASS, both permission denied, exit 1 |
| Password-backed login for student2 | Successful | PASS: `su - student2 -c 'id'` returned uid 1001 |
| Password-backed login for faculty2 | Successful | PASS: `su - faculty2 -c 'id'` returned uid 1002 |
| Password-backed login for student4 | Successful | PASS: `su - student4 -c 'id'` returned uid 1003 |

The script groups paired operations into checks, hence the table has more rows than the 12 reported PASS lines. The final directory modes are `/labdata` 750, `/facultydata` 770, and `/studentdata` 750.
