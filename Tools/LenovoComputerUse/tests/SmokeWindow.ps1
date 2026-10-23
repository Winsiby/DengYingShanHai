param([Parameter(Mandatory=$true)][string]$StatePath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$script:statePath = [IO.Path]::GetFullPath($StatePath)
$script:clicks = 0
$script:scrolls = 0
$script:dragPixels = 0
$script:lastKey = ''
$form = New-Object System.Windows.Forms.Form
$form.Text = 'Lenovo Computer Use Test'
$form.StartPosition = 'CenterScreen'
$form.ClientSize = New-Object System.Drawing.Size(640, 440)
$form.TopMost = $false
$form.KeyPreview = $true
$label = New-Object System.Windows.Forms.Label
$label.Text = 'Personal desktop plugin: isolated smoke test'
$label.Location = New-Object System.Drawing.Point(20, 20)
$label.Size = New-Object System.Drawing.Size(600, 30)
$text = New-Object System.Windows.Forms.TextBox
$text.AccessibleName = 'Test text input'
$text.Location = New-Object System.Drawing.Point(20, 65)
$text.Size = New-Object System.Drawing.Size(590, 140)
$text.Multiline = $true
$text.Font = New-Object System.Drawing.Font('Microsoft YaHei', 14)
$button = New-Object System.Windows.Forms.Button
$button.Text = 'Click test'
$button.AccessibleName = 'Click test'
$button.Location = New-Object System.Drawing.Point(20, 230)
$button.Size = New-Object System.Drawing.Size(180, 50)
$panel = New-Object System.Windows.Forms.Panel
$panel.AccessibleName = 'Drag test panel'
$panel.Location = New-Object System.Drawing.Point(230, 230)
$panel.Size = New-Object System.Drawing.Size(370, 150)
$panel.BackColor = [System.Drawing.Color]::LightSteelBlue
$panel.TabStop = $true
$resultLabel = New-Object System.Windows.Forms.Label
$resultLabel.Location = New-Object System.Drawing.Point(20, 395)
$resultLabel.Size = New-Object System.Drawing.Size(600, 30)
$form.Controls.AddRange(@($label, $text, $button, $panel, $resultLabel))
function Write-TestState {
    $resultLabel.Text = "Clicks: $script:clicks; drag: $script:dragPixels; scroll: $script:scrolls; key: $script:lastKey"
    [ordered]@{ text=$text.Text; clicks=$script:clicks; drag_pixels=$script:dragPixels;
        scrolls=$script:scrolls; last_key=$script:lastKey; pid=$PID; panel_width=$panel.ClientSize.Width } |
        ConvertTo-Json -Compress | Set-Content -LiteralPath $script:statePath -Encoding UTF8
}
$text.Add_TextChanged({ Write-TestState })
$button.Add_Click({ $script:clicks++; Write-TestState })
$panel.Add_MouseDown({ param($sender,$event) $panel.Focus(); $script:dragStart=$event.Location })
$panel.Add_MouseUp({ param($sender,$event)
    if ($null -ne $script:dragStart) {
        $script:dragPixels=[Math]::Abs($event.X-$script:dragStart.X)+[Math]::Abs($event.Y-$script:dragStart.Y)
        Write-TestState
    }
})
$panel.Add_MouseWheel({ param($sender,$event) $script:scrolls += $event.Delta / 120; Write-TestState })
$form.Add_KeyDown({ param($sender,$event) $script:lastKey=$event.KeyCode.ToString(); Write-TestState })
$form.Add_Shown({ $form.Activate(); Write-TestState })
[System.Windows.Forms.Application]::Run($form)
$form.Dispose()
