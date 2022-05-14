if (Test-Path -Path './FTA-1.0.0.zip') {
	pip install setuptools --upgrade
	pip install './FTA-1.0.0.zip'
	python -m FTA -h
	powershell.exe
}
else {
	Write-Output "FTA-1.0.0.zip not found"
	Write-Host -NoNewLine 'Press any key to continue...';
	$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
}