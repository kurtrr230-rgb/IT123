# Lab Report 2 - Week 3

## Scope and current status

This lab covers user and group management and directory permissions on Ubuntu. The student requested Ubuntu only for now. Windows Server tasks in the supplied guide are deferred, so this is not a completed report for the guide's full two-platform assessment.

The existing administrator account is `kadmin`. Its password reset completed and an authenticated shell was observed. A direct guest screenshot identified Ubuntu 26.04.1 LTS; the earlier Week 2 draft incorrectly transcribed its boot banner as 24.04.1 LTS.

Week 3 setup and verification ran on the Ubuntu VM. The verification script reported 12 passed checks, 0 failed checks, and exit code 0. Password-backed logins also succeeded for all three new users. Configuration screenshots and the raw access-test output are saved alongside this report.

## Verified Ubuntu configuration

| User | Additional group | Directory | Owner:group | Mode |
| --- | --- | --- | --- | --- |
| student2 | labusers | /labdata | root:labusers | 770 initially; 750 after removing group write |
| faculty2 | facultygrp | /facultydata | root:facultygrp | 770 |
| student4 | studentgrp | /studentdata | root:studentgrp | 750 |

Set student2's comment to `Test account for Week 3 Lab`. Directory execute permission is required to traverse the directory; therefore group read-only access uses `r-x`, not `r--`. Root retains administrative access. Ordinary users outside the assigned group receive no access.

## Procedure executed

1. Inspect existing users, groups, and target directories before making changes.
2. Create the three users with home directories, then create and assign the groups above.
3. Set account passwords interactively. Keep credentials out of screenshots, notes, and Git.
4. Create the three root-owned directories with the specified group ownership and modes.
5. Create a root-owned sample file in each directory to support read tests.
6. Run tests using each user's identity. Record the initial successful student2 write in /labdata.
7. Change /labdata from mode 770 to 750. Repeat the write test and verify denial, while confirming reading still works.
8. Verify faculty2 can read/write /facultydata and student4 can read but cannot write /studentdata.
9. Verify cross-group access is denied. Log in as each user to check authentication separately from authorization.
10. Capture configuration screenshots and copy the test output into the Week 3 repository folder.

## Evidence collected

- [User records and group memberships](screenshots/01-users-and-groups.png), including student2's comment.
- [Final directory ownership and modes](screenshots/02-directory-permissions.png), with the mode transition recorded in the [test output](verification-output.txt).
- Allowed and denied operations recorded in [verification results](verification.md) and the raw test output.
- Password-backed logins for student2, faculty2, and student4, observed in the VM SSH session. Those login outputs are summarized in the report; they were not captured as screenshots.

`runuser` tests authorization under a user's identity, not that user's password. Each password-backed login was therefore verified separately with `su` as the non-root kadmin user.

## Source

Six student-supplied photographs of the Week 3 user/group-management guide, verification tasks, exercise, deliverables, and rubric. Observed outcomes are distinguished from assignment requirements in the verification results.
