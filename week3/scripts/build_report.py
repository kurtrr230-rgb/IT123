from pathlib import Path
from io import BytesIO

import pypdfium2 as pdfium
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

root = Path(__file__).resolve().parents[1]
out = root / 'report'
out.mkdir(exist_ok=True)
pdf = out / 'IT123_Week3_Ubuntu_Lab_Report.pdf'
s = getSampleStyleSheet()
s['Title'].textColor = colors.HexColor('#153047')
s['Title'].alignment = 0
s['Title'].fontSize = 24
s['Title'].leading = 29
s['Heading2'].textColor = colors.HexColor('#153047')
s['BodyText'].fontSize = 10
s['BodyText'].leading = 14
s['BodyText'].spaceAfter = 8
s['Normal'].fontSize = 9
s['Normal'].leading = 12
story = []

def p(text, style='BodyText'):
    story.append(Paragraph(text, s[style]))

def table(rows, widths):
    entries = [[Paragraph(cell, s['Normal']) for cell in row] for row in rows]
    item = Table(entries, colWidths=widths, repeatRows=1)
    item.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DDEAF3')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(item)

def figure(filename, caption):
    path = root / 'screenshots' / filename
    crop_height = 430 if filename.startswith('03-') else 170
    with PILImage.open(path) as original:
        region = original.crop((0, 0, original.width, crop_height))
        data = BytesIO()
        region.save(data, format='PNG')
    data.seek(0)
    story.append(Image(data, width=495, height=495 * crop_height / original.width))
    p(caption, 'Normal')

def footer(canvas, doc):
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#466177'))
    canvas.drawString(50, 28, 'IT 123 | Week 3 | Ubuntu lab')
    canvas.drawRightString(545, 28, str(doc.page))

p('IT 123 - Lab Report 2', 'Title')
p('Ubuntu User, Group, and Permission Management', 'Heading2')
p('<b>Scope:</b> Ubuntu Server only, as directed by the student. No Windows Server VM was available. The Windows portion of the course guide remains outstanding. Student name and section were not supplied.')
p('1. Objective', 'Heading2')
p('Create local users and groups, assign directory access, and verify that permitted operations succeed while unauthorized operations fail.')
p('2. Environment and setup', 'Heading2')
p('Existing VirtualBox guest: Ubuntu 26.04.1 LTS. The administrator account kadmin was already available. The setup script checked that target users, groups, and directories did not exist, then created student2, faculty2, and student4 with home directories. Passwords were set through hidden prompts and are not recorded in this report.')
table([
    ['Account / group', 'Directory / ownership', 'Mode'],
    ['student2 / labusers', '/labdata<br/>root:labusers', '770, then 750'],
    ['faculty2 / facultygrp', '/facultydata<br/>root:facultygrp', '770'],
    ['student4 / studentgrp', '/studentdata<br/>root:studentgrp', '750'],
], [157, 222, 116])
story.append(Spacer(1, 7))
p('The student2 account comment is "Test account for Week 3 Lab". Each directory contains a root-owned sample file. The final /labdata mode is 750: group members can read and traverse, but cannot write. Its initial mode 770 allowed the required before-and-after write test.')
p('3. Procedure', 'Heading2')
p('The setup script created accounts and groups, assigned supplementary groups, and applied root ownership and modes. The verification script ran commands under each new user identity, recorded exit codes, and changed /labdata from 770 to 750 between the initial and final checks. Separate password-backed `su` sessions verified that each account could authenticate.')
p('The complete commands are in scripts/setup_ubuntu.sh and scripts/verify_ubuntu.sh. The original test output is in verification-output.txt.')
story.append(PageBreak())
p('4. Verification results', 'Heading2')
p('<b>Result:</b> 12 access checks passed, 0 failed, script exit code 0. Each of the three password-backed account logins also succeeded.')
table([
    ['Test', 'Expected', 'Observed'],
    ['student2 reads /labdata at 770 and 750', 'Allow', 'PASS / exit 0'],
    ['student2 creates a file at 770', 'Allow', 'PASS / exit 0'],
    ['student2 creates a file at 750', 'Deny', 'PASS / permission denied'],
    ['faculty2 reads and writes /facultydata', 'Allow', 'PASS / exit 0'],
    ['student4 reads /studentdata', 'Allow', 'PASS / exit 0'],
    ['student4 creates or edits in /studentdata', 'Deny', 'PASS / permission denied'],
    ['Cross-group directory access', 'Deny', 'PASS / permission denied'],
    ['student2, faculty2, student4 logins', 'Allow', 'PASS / correct user IDs'],
], [274, 78, 143])
story.append(Spacer(1, 10))
p('5. Interpretation', 'Heading2')
p('The before-and-after /labdata test demonstrates that removing group write permission blocks new files while preserving read access. The separate faculty and student directories allow their designated groups the requested access. Cross-group attempts fail. Password-backed `su` logins validate authentication; `runuser` tests in the script validate file authorization.')
p('6. Evidence and limitations', 'Heading2')
p('The following screenshots were captured directly from the Ubuntu VM after setup and testing. The raw test log records the initial and final /labdata modes, allowed operations, and permission-denied errors. The login tests were observed in the live terminal session and summarized here; separate login screenshots were not captured. Windows Server work is outside this Ubuntu-only report.')
p('Source: six student-provided photographs of the IT 123 Week 3 laboratory guide and rubric. The guide includes Windows Server tasks as well as Ubuntu tasks.')
story.append(PageBreak())
p('Appendix A - User and group evidence', 'Heading2')
figure('01-users-and-groups.png', 'Figure 1. User IDs, supplementary groups, home directories, and the student2 comment. Screenshot cropped to its terminal output; the full capture is in screenshots/.')
story.append(Spacer(1, 20))
p('Appendix B - Directory permission evidence', 'Heading2')
figure('02-directory-permissions.png', 'Figure 2. Final ownership and modes. kadmin receives Permission denied when listing the restricted directories. Screenshot cropped to its terminal output; the full capture is in screenshots/.')
story.append(Spacer(1, 20))
p('Appendix C - Access-test evidence', 'Heading2')
figure('03-access-test-results.png', 'Figure 3. Successful and denied operations from the Ubuntu test run, ending with zero failed checks. Screenshot cropped to the test output; the full capture is in screenshots/.')

SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=50, rightMargin=50,
                  topMargin=45, bottomMargin=50).build(
    story, onFirstPage=footer, onLaterPages=footer)
qa = root.parent / 'tmp' / 'week3-pdf'
qa.mkdir(parents=True, exist_ok=True)
doc = pdfium.PdfDocument(str(pdf))
for i, page in enumerate(doc):
    page.render(scale=1.2).to_pil().save(qa / f'page-{i + 1}.png')
print(f'{pdf}\nPages: {len(doc)}')
