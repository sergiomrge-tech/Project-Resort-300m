param([string]$Tool,[string]$Arguments='{}',[string]$Toolset='EditorToolset.EditorAppToolset',[string]$ImagePath='D:\ProjectResort_300m_CompactPass\UnrealProject\Saved\half_map_viewport.png')
$ErrorActionPreference='Stop'
$uri='http://127.0.0.1:8000/mcp';$h=@{Accept='application/json, text/event-stream'}
$i=Invoke-WebRequest -Uri $uri -Method Post -Headers $h -ContentType 'application/json' -Body '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"ProjectResort-Codex","version":"1.0"}}}'
$h['Mcp-Session-Id']=(($i.Headers['Mcp-Session-Id'] -join '').Trim())
$null=Invoke-WebRequest -Uri $uri -Method Post -Headers $h -ContentType 'application/json' -Body '{"jsonrpc":"2.0","method":"notifications/initialized"}'
$p=@{toolset_name=$Toolset;tool_name=$Tool;arguments=($Arguments|ConvertFrom-Json -AsHashtable)}
$b=@{jsonrpc='2.0';id=2;method='tools/call';params=@{name='call_tool';arguments=$p}}|ConvertTo-Json -Depth 20 -Compress
$r=Invoke-WebRequest -Uri $uri -Method Post -Headers $h -ContentType 'application/json' -Body $b
$j=$r.Content|ConvertFrom-Json
foreach($c in $j.result.content){if($c.type -eq 'image'){[IO.File]::WriteAllBytes($ImagePath,[Convert]::FromBase64String($c.data));Write-Output ('Screenshot: '+$ImagePath)}else{$v=$null;try{$v=$c.text|ConvertFrom-Json -ErrorAction Stop}catch{};if($v.returnValue.image.data){[IO.File]::WriteAllBytes($ImagePath,[Convert]::FromBase64String($v.returnValue.image.data));Write-Output ('Screenshot: '+$ImagePath);Write-Output ($v.returnValue.cameraLocation|ConvertTo-Json -Compress)}else{Write-Output $c.text}}}
