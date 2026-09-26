from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report'
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / 'IT123_Week2_Lab_Report_DRAFT.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', fontName='Helvetica-Bold', fontSize=27, leading=32, textColor=colors.HexColor('#153047'), spaceAfter=16))
styles.add(ParagraphStyle(name='Subtitle2', fontSize=12, leading=17, textColor=colors.HexColor('#466177'), spaceAfter=15))
styles['BodyText'].fontSize = 10
styles['BodyText'].leading = 15
styles['BodyText'].spaceAfter = 9
styles['Heading2'].textColor = colors.HexColor('#153047')
styles['Heading2'].spaceBefore = 14
styles['Heading2'].spaceAfter = 9
styles.add(ParagraphStyle(name='Caption2', fontSize=9, leading=13, textColor=colors.HexColor('#466177'), spaceAfter=12))

story=[]
def p(text, style='BodyText'):
    story.append(Paragraph(text,styles[style]))
def photo(name, caption):
    path=ROOT/'screenshots'/name
    w,h=ImageReader(str(path)).getSize()
    story.append(Image(str(path),width=491,height=491*h/w))
    story.append(Spacer(1,8))
    p(caption,'Caption2')
def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#D4DEE6'))
    canvas.line(52,43,543,43)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#466177'))
    canvas.drawString(52,29,'IT 123 | Week 2 | Evidence draft - incomplete')
    canvas.drawRightString(543,29,str(doc.page))

p('IT 123 / LAB REPORT 1','Subtitle2')
p('Virtual Machine<br/>Configuration &amp;<br/>Ubuntu Account Recovery','CoverTitle')
p('Week 2 laboratory | Inspection date: 26 September 2026','Subtitle2')
p('<b>DRAFT - NOT READY FOR SUBMISSION</b><br/>Student name and section have not yet been supplied. Password recovery, successful login verification, Windows Server evidence, and the GitHub push remain outstanding.')
p('1. Objective and scope','Heading2')
p('The laboratory guide asks students to install and configure Windows Server and Ubuntu Server in VirtualBox, document VM resources and major steps, and publish the documentation to GitHub. The student reports that the Ubuntu VM was already set up in Lab 1. This report records the existing configuration and the checks performed during this session.')
p('2. Verified Ubuntu configuration','Heading2')
rows=[['Setting','Observed value'],['VM name','ubuntu_server'],['Boot banner','Ubuntu 24.04.1 LTS'],['Memory / processors','2048 MB / 2 virtual CPUs'],['Virtual disk','VDI, 25.00 GB shown by VirtualBox'],['Network','NAT; adapter cable connected'],['Firmware / graphics','BIOS / VMSVGA, 16 MB video memory'],['Optical drive','Empty'],['Existing snapshot','Snapshot 1'],['Boot result','Console login prompt reached']]
t=Table(rows,colWidths=[160,331],hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#153047')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#EDF3F7'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP')]))
story.append(t)
story.append(Spacer(1,12))
p('Configuration difference: the guide requests a 30 GB Ubuntu disk; the existing disk is 25 GB. Its capacity was not changed. The snapshot name is verified, but its contents and clean-install status are not verified.','Caption2')
story.append(PageBreak())
p('3. Configuration and boot evidence','Heading2')
photo('01-virtualbox-settings.png','Figure 1. Existing VirtualBox settings, showing RAM, CPUs, virtual disk, and NAT networking.')
photo('02-ubuntu-login-prompt.png','Figure 2. Ubuntu console after boot. Reaching a login prompt confirms that the guest boots; it does not establish a successful user login.')
p('Verification performed','Heading2')
p('The registered Ubuntu VM was inspected and started in VirtualBox. It reached the Ubuntu 24.04.1 LTS console login prompt. An attempt was made to open the GRUB recovery menu during a restart, but the normal boot continued. No password change has yet been confirmed.')
story.append(PageBreak())
p('4. Installation history and evidence limits','Heading2')
p('The original installation predates this session. The supplied photographs describe the assignment; they do not show the student performing the installation. Original installation choices and screenshots cannot be reconstructed as observed facts. Only Ubuntu is currently registered in VirtualBox; the status of any Windows Server installation requires clarification.')
p('5. Remaining completion steps','Heading2')
for text in [
    'Open the Ubuntu GRUB recovery menu, identify the existing user account, and complete the password reset.',
    'Sign in to Ubuntu and capture evidence of the successful login. Verify networking and the OpenSSH service.',
    'Supply the student name, section, and GitHub repository destination.',
    'Confirm Windows Server status and supply its configuration and login evidence where applicable.',
    'Add original installation screenshots if available, then finalize the PDF and Markdown notes.',
    'Commit the report and screenshots under week2 and push to the confirmed GitHub repository.'
]: p('&#8226; '+text)
p('6. Current conclusion','Heading2')
p('The existing Ubuntu VM boots to its login prompt and has 2 GB RAM, 2 virtual CPUs, and NAT networking. The disk is smaller than the guide specifies. Account access, network service operation, and the Windows Server portion remain unverified. The lab is therefore not yet complete.')
p('Source and repository status','Heading2')
p('Source: student-supplied photographs of the IT 123 - Week 2 Laboratory Guide. The guide requires a PDF report, installation documentation, screenshots, a configuration summary, and a GitHub upload.')
p('Local evidence is saved under week2/screenshots and notes under week2/lab_notes.md. The current repository has no remote configured. No commit or push has been performed. Credentials and VM disk images are excluded from the intended upload.')

SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=46,bottomMargin=57,title='IT 123 Week 2 Lab Report - Evidence Draft',author='').build(story,onFirstPage=footer,onLaterPages=footer)
qa=ROOT.parent/'tmp'/'pdfs'
qa.mkdir(parents=True,exist_ok=True)
doc=pdfium.PdfDocument(str(PDF))
for i,page in enumerate(doc):
    page.render(scale=1.25).to_pil().save(qa/f'page-{i+1}.png')
print(f'{PDF}\nPages: {len(doc)}')
