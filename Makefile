ui: gui/ui_main.py gui/ui_install_prompt.py gui/ui_install_progress.py

gui/ui_%.py : gui/%.ui
	pyuic5 $< > $@
