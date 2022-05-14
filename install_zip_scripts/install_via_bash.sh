$FILE='./FTA-1.0.0.zip'
if [ -f "$FILE" ]; then
	pip install setuptools --upgrade
	pip install $FILE
	python -m FTA -h
    $SHELL
else
	echo "FTA-1.0.0.zip not found"
	read -p "Press enter to continue"
fi