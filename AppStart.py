from os.path import join
import appstart.SettingsConfigure as sc

def mainMenu():
	print("Please select from the menu below:")

	print("0 - Scrape Webstation & get csv output")
	print("1 - Run vb Macro for actual times")
	print("2 - Transfer Files to UKG")

	try:
		menuOption = int(input("> "))
	except ValueError:
		print("Option not supported")
		quit()

	return menuOption

if __name__ == '__main__':
	configurationPath = join('.settings', 'config.json')
	jsonConfig = sc.get_Configuration(configurationPath)
	json_Settings = jsonConfig["AppSettings"]

	menuOption = mainMenu()
	options = ["Scrapped", "vbRan", "Xferred", "Nu uhhh"]

	try:
		print(options[menuOption])
	except IndexError:
		print("Option unavailable.")
		exit(0)