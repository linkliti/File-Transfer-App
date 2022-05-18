$FILE='./FTA-1.0.1.zip'
if (Test-Path -Path $FILE) {
	pip install setuptools --upgrade
	pip install $FILE
	python -m FTA -h
	powershell.exe
}
else {
	Write-Output "FTA archive not found"
	Write-Host -NoNewLine 'Press any key to continue...';
	$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
}