"""Build the Week 6 Ubuntu-only PDF from recorded VM evidence."""

from io import BytesIO
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "IT123_Week6_Ubuntu_Network_Lab.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
STYLES = getSampleStyleSheet()
NAVY = colors.HexColor("#17324d")
BLUE = colors.HexColor("#216895")
STYLES.add(ParagraphStyle(name="ReportTitle", parent=STYLES["Title"], fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=NAVY, spaceAfter=8))
STYLES.add(ParagraphStyle(name="ReportSub", parent=STYLES["Normal"], fontSize=11, leading=15, textColor=BLUE, spaceAfter=12))
STYLES.add(ParagraphStyle(name="Section", parent=STYLES["Heading2"], fontSize=12, leading=15, textColor=NAVY, spaceBefore=11, spaceAfter=5))
STYLES.add(ParagraphStyle(name="Body9", parent=STYLES["BodyText"], fontSize=9.2, leading=13, spaceAfter=7))
STYLES.add(ParagraphStyle(name="Caption", parent=STYLES["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#40556a"), spaceBefore=3, spaceAfter=10))
STYLES.add(ParagraphStyle(name="Small", parent=STYLES["Normal"], fontSize=8, leading=11, spaceAfter=4))
STYLES.add(ParagraphStyle(name="CodeBlock", parent=STYLES["Code"], fontName="Courier", fontSize=8.2, leading=11, leftIndent=9, rightIndent=6, borderColor=colors.HexColor("#d9e5ec"), borderWidth=0.4, borderPadding=7, backColor=colors.HexColor("#f6f9fb"), spaceBefore=3, spaceAfter=8))
STORY = []


def para(value: str, style: str = "Body9") -> None:
    STORY.append(Paragraph(value, STYLES[style]))


def section(value: str) -> None:
    para(value, "Section")


def code(value: str) -> None:
    STORY.append(Preformatted(value, STYLES["CodeBlock"]))


def table(rows: list[list[str]], widths: list[int]) -> None:
    cells = [[Paragraph(cell, STYLES["Small"]) for cell in row] for row in rows]
    item = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    item.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3edf5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#aac2d3")),
    ]))
    STORY.append(item)


def figure(filename: str, crop: tuple[int, int, int, int], caption: str) -> None:
    path = ROOT / "screenshots" / filename
    with PILImage.open(path) as original:
        frame = original.crop(crop)
        image_bytes = BytesIO()
        frame.save(image_bytes, "PNG")
    image_bytes.seek(0)
    width = 490
    height = width * frame.height / frame.width
    STORY.append(KeepTogether([
        Image(image_bytes, width=width, height=height),
        Paragraph(caption, STYLES["Caption"]),
    ]))


def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#62778a"))
    canvas.drawString(48, 27, "IT 123  |  Week 6  |  Ubuntu Server network lab")
    canvas.drawRightString(A4[0] - 48, 27, f"Page {doc.page}")


para("IT 123 — Week 6 Lab Report", "ReportTitle")
para("Network configuration and management • Ubuntu Server only", "ReportSub")
para("<b>Student:</b> Not provided &nbsp;&nbsp; <b>VM:</b> ubuntu_server &nbsp;&nbsp; <b>OS:</b> Ubuntu 26.04.1 LTS &nbsp;&nbsp; <b>Date:</b> 27 September 2026")
para("<b>Outcome:</b> The existing VM was changed from DHCP to a working static IPv4 address, tested for routing, internet access, and DNS, then returned to its original DHCP configuration. The final DHCP state was verified.")

section("Network choice")
para("The guide specifies <b>192.168.1.150/24</b> and gateway <b>192.168.1.1</b>. This VM is connected to a VirtualBox NAT network <b>10.0.2.0/24</b>, so those guide values would not reach its actual gateway. The temporary static test used <b>10.0.2.150/24</b>, gateway <b>10.0.2.2</b>, and DNS <b>8.8.8.8 / 8.8.4.4</b>. This tested the same netplan procedure without disconnecting the VM.")

section("Step 1 — Inspect and back up DHCP")
code("ip -4 a show dev enp0s3\nip route\nresolvectl dns enp0s3\ncat /etc/netplan/00-installer-config.yaml")
para("The starting address was <b>10.0.2.15/24</b> from DHCP; the default route used <b>10.0.2.2</b>. The original netplan file was saved and a VirtualBox snapshot named <b>Week6-before-network</b> was taken before edits.")
figure("01-netplan-before.png", (0, 0, 690, 250), "Figure 1. Original netplan file with DHCP enabled. Full console capture and baseline output are in the repository.")

STORY.append(PageBreak())
section("Step 2 — Apply and verify a static address")
para("The saved static file was installed at <b>/etc/netplan/00-installer-config.yaml</b>. <b>sudo netplan generate</b> checked the file, then <b>sudo netplan try --timeout 120</b> applied it with automatic rollback available. The new connection was checked before the trial was accepted.")
code("enp0s3:\n  dhcp4: false\n  addresses: [10.0.2.150/24]\n  routes: [{to: default, via: 10.0.2.2}]\n  nameservers:\n    addresses: [8.8.8.8, 8.8.4.4]")
figure("02-netplan-static.png", (0, 0, 710, 325), "Figure 2. Temporary static netplan configuration and active 10.0.2.150/24 address.")
section("Step 3 — Test the static connection")
code("ping -c 4 10.0.2.2\nping -c 4 8.8.8.8\nping -4 -c 4 google.com\nnslookup google.com\ntraceroute -4 -m 12 -q 1 -w 1 google.com\nss -tuln")
table([
    ["Check", "Observed result"],
    ["Gateway / public IP / domain ping", "4 replies out of 4 for each target; 0% loss"],
    ["DNS lookup", "google.com resolved to IPv4 and IPv6 addresses"],
    ["Traceroute", "Hop 1 was 10.0.2.2; hops 2–12 did not answer"],
    ["Listening sockets", "SSH on port 22 and local DNS listeners were present"],
], [205, 290])

STORY.append(PageBreak())
section("Static connection evidence")
para("The internet and name pings succeeded even though intermediate traceroute probes did not receive replies. Asterisks in traceroute mean no response to those specific probes; they do not establish that ordinary traffic failed.")
figure("03-ping.png", (0, 0, 830, 500), "Figure 3. Gateway, public-IP, and domain-name ping results from the static configuration.")
figure("04-dns-traceroute.png", (0, 0, 700, 405), "Figure 4. DNS lookup and traceroute from the static configuration. The first hop is the VirtualBox NAT gateway.")

STORY.append(PageBreak())
section("Step 4 — Restore DHCP and check the final state")
para("The saved original file was put back, syntax-checked, and applied using <b>sudo netplan try --timeout 120</b>. Before acceptance, the VM showed the DHCP address <b>10.0.2.15/24</b>, default gateway <b>10.0.2.2</b>, successful public-IP ping, and successful DNS resolution. The active file matched the original backup exactly.")
figure("05-dhcp-restored.png", (0, 0, 740, 265), "Figure 5. Restored original DHCP netplan file, active address, and default route.")
table([
    ["Final verification", "Observed result"],
    ["Gateway 10.0.2.2", "4 of 4 replies"],
    ["Internet 8.8.8.8", "4 of 4 replies"],
    ["google.com ping", "4 of 4 replies"],
    ["nslookup google.com", "IPv4 and IPv6 addresses returned"],
], [205, 290])
STORY.append(Spacer(1, 7))
section("Scope and evidence")
para("Only one Ubuntu VM was available. It demonstrated the static and DHCP states sequentially; a simultaneous Server A-to-Server B ping was <b>not performed</b>. A second VM on a shared network is required for that part of the exercise. Optional Windows Server work was excluded by request. Temporary host-side SSH forwarding rules used during the lab were removed.")
para("Repository folder <b>Week6/</b> contains this report, the full unedited text outputs in <b>evidence/</b>, the complete screenshots in <b>screenshots/</b>, the tested static netplan file in <b>scripts/</b>, and a step-by-step explanation in <b>lab_notes.md</b>.")

doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=48, rightMargin=48, topMargin=43, bottomMargin=47)
doc.build(STORY, onFirstPage=footer, onLaterPages=footer)

render_dir = ROOT.parent / "tmp" / "week6-pdf-qa"
render_dir.mkdir(parents=True, exist_ok=True)
pdf = pdfium.PdfDocument(str(OUTPUT))
for page_number, page in enumerate(pdf, 1):
    page.render(scale=1.25).to_pil().save(render_dir / f"page-{page_number}.png")
print(f"Created {OUTPUT}; {len(pdf)} pages; render at {render_dir}")
