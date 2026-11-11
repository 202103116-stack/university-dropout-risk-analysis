# PowerPoint로 발표 PPTX를 PDF로 내보낸다(포함된 글꼴로 렌더링).
# 사용: powershell -ExecutionPolicy Bypass -File slides/export_pdf.ps1
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$pptx = Join-Path $here '14조_발표.pptx'
$pdf = Join-Path $here '14조_발표.pdf'
$app = New-Object -ComObject PowerPoint.Application
try {
    $p = $app.Presentations.Open($pptx, $true, $false, $false)
    $p.SaveAs($pdf, 32)   # 32 = ppSaveAsPDF
    "slides: " + $p.Slides.Count
    $p.Close()
} finally {
    $app.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
}
