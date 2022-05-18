$FILE='./FTA-1.0.1.zip'
if [ -f "$FILE" ]; then
	pip install setuptools --upgrade
	pip install $FILE
	python -m FTA -h
    $SHELL
else
	echo "FTA archive not found"
	read -p "Press enter to continue"
fi