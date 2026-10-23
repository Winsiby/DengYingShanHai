$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
try {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class LenovoUiDpi {
    [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
    [DllImport("user32.dll")] public static extern IntPtr SetThreadDpiAwarenessContext(IntPtr value);
}
'@
    [LenovoUiDpi]::SetProcessDpiAwarenessContext([IntPtr](-4)) | Out-Null
    [LenovoUiDpi]::SetThreadDpiAwarenessContext([IntPtr](-4)) | Out-Null
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $request = [Console]::In.ReadLine() | ConvertFrom-Json
    $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][long]$request.hwnd)
    if ($root.Current.ProcessId -ne [int]$request.pid) { throw 'Window identity changed' }
    $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue(@($root, 0))
    $nodes = New-Object System.Collections.Generic.List[object]
    while ($queue.Count -gt 0 -and $nodes.Count -lt 200) {
        $item = $queue.Dequeue()
        $element = $item[0]
        $depth = [int]$item[1]
        try {
            $current = $element.Current
            # Do not expose password contents or labels from protected input.
            $name = if ($current.IsPassword) { '[password field]' } else { $current.Name }
            if ($name.Length -gt 500) { $name = $name.Substring(0, 500) }
            $r = $current.BoundingRectangle
            $nodes.Add([ordered]@{
                name = $name
                automation_id = $current.AutomationId
                control_type = $current.ControlType.ProgrammaticName
                enabled = $current.IsEnabled
                offscreen = $current.IsOffscreen
                password = $current.IsPassword
                depth = $depth
                rect = @{ left=$r.Left; top=$r.Top; width=$r.Width; height=$r.Height }
            })
            if ($depth -lt 6) {
                $child = $walker.GetFirstChild($element)
                $siblings = 0
                while ($null -ne $child -and $siblings -lt 200 -and $queue.Count -lt 400) {
                    $queue.Enqueue(@($child, ($depth + 1)))
                    $child = $walker.GetNextSibling($child)
                    $siblings++
                }
            }
        } catch [System.Windows.Automation.ElementNotAvailableException] {
            continue
        }
    }
    [ordered]@{ nodes=$nodes.ToArray(); truncated=($queue.Count -gt 0); coordinates='physical desktop pixels' } |
        ConvertTo-Json -Depth 8 -Compress | ForEach-Object { [Console]::WriteLine($_) }
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
