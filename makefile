#Makefile
del_vivado_jou_log:
	rm -R *.jou
	rm -R *.log

run:
	python3 run.py

open_gui_proj:
	python3 open_vivado.py
	
get_all_code_files:
	python3 get_all_code_files.py

get_all_ip_files:
	python3 get_all_ip_files.py
