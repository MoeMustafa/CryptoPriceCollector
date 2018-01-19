
from quadriga import QuadrigaClient
from chalice import Chalice
import requests
import json

app = Chalice(app_name='CPriceCollector')

app.debug = True


dicCanadaAreaCode = {
	"403" : 'AB',
	"587" : 'AB',
	"780" : 'AB',
	"825" : 'AB',
	"236" : 'BC',
	"250" : 'BC',
	"604" : 'BC',
	"778" : 'BC',
	"204" : 'MB',
	"431" : 'MB',
	"506" : 'NB',
	"709" : 'NL', 
	"879" : 'NL',
	"867" : 'NT',
	"782" : 'NS',
	"902" : 'NS',
	"867" : 'NU',
	"226" : 'ON',
	"249" : 'ON',
	"289" : 'ON',
	"343" : 'ON',
	"365" : 'ON',
	"416" : 'ON',
	"437" : 'ON',
	"519" : 'ON',
	"548" : 'ON',
	"613" : 'ON',
	"647" : 'ON',
	"705" : 'ON',
	"807" : 'ON',
	"905" : 'ON',
	"782" : 'NB',
	"902" : 'NB',
	"367" : 'QC',
	"418" : 'QC',
	"438" : 'QC',
	"450" : 'QC',
	"514" : 'QC',
	"579" : 'QC',
	"581" : 'QC',
	"819" : 'QC',
	"873" : 'QC',
	"306" : 'SK',
	"639" : 'SK',
	"867" : 'YT'
}


class PhoneValidator(object):
	'''
	Validate provided phone number, without country code

	PhoneValidator only look up for Canadian phone, currently 
	it doesn't support other countries

	PhoneValidator class only accept 10 digits integer, otheriwse 
	validation will fale.

	Ex1:  5191234567

	returns True 

	Ex2:  1234567890

	returns False

	'''
	def __init__(self, phonenumber):
		self.phonenumber = phonenumber

	def areaCodeLookup(self, area_code):
		# Validate area present is area code dictionary
		try:
			dicCanadaAreaCode[area_code]
			return True
		except:
			return False

	def validPhoneNumber(self):
		return len(str(self.phonenumber)) == 10

	def sliceAreaCode(self):
		return str(self.phonenumber)[:3]

	def mobileVerifer(self):
		if self.validPhoneNumber():
			# Check first 3 digits 
			area_code = self.sliceAreaCode()
			print "Verifing area code for {}".format(area_code)
			return self.areaCodeLookup(area_code)
		else:
			return False

	def phoneProvince(self):
		if self.validPhoneNumber():
			area_code = self.sliceAreaCode()
			return dicCanadaAreaCode[area_code]
		else:
			return False




def deep_search(needles, haystack):
	# Find key value in json file 
    found = {}
    if type(needles) != type([]):
        needles = [needles]

    if type(haystack) == type(dict()):
        for needle in needles:
            if needle in haystack.keys():
                found[needle] = haystack[needle]
            elif len(haystack.keys()) > 0:
                for key in haystack.keys():
                    result = deep_search(needle, haystack[key])
                    if result:
                        for k, v in result.items():
                            found[k] = v
    elif type(haystack) == type([]):
        for node in haystack:
            result = deep_search(needles, node)
            if result:
                for k, v in result.items():
                    found[k] = v
    return found

def get_url_response(url):
 	response = requests.get(url, verify=True) 
	if response.status_code != 200:
		print('Status:', response.status_code, 'Problem with the request. Exiting.')
		return
	return response.json()

def coinbase_price(currency='CAD'):
	coinbase_url = "https://api.coinbase.com/v2/prices/spot?currency={}".format(currency)
	response = get_url_response(coinbase_url)
	value = deep_search('amount',response)
	print ('Coinbase : {}').format(value['amount'])
	return "Coinbase " + str(value['amount']) + currency

def bitfinex_price():
	# Check Bitfinex 
	return "Bitfinex " + str(Bitfinex().get_current_price()) + "USD"

def quadrigacx_price(fiatCurrency='cad',cryptoCurrency='btc'):
	# Check quadrigacx 
	#qd_url = "https://api.quadrigacx.com/v2/ticker?book=eth_cad"
	try:
		qd_url = "https://api.quadrigacx.com/v2/ticker?book={}_{}".format(cryptoCurrency, fiatCurrency)
		response = get_url_response(qd_url)
		print ('quadrigacx : {}').format(response['last'])
		return "QuadrigaCX " + str(response['last']) + fiatCurrency.upper()
	except Exception as e:
		return e


@app.route('/')
def index():
	blockchain_url = 'https://blockchain.info/ticker'
	try:
		res_price = get_url_response(blockchain_url) 
		#cad_price = json.loads(res_price)
		purchase_price_cad = int(res_price['CAD']['15m']) * 1.12
		purchase_price_usd = int(res_price['USD']['15m']) * 1.12
		return json.dumps({'CAD':purchase_price_cad,'USD':purchase_price_usd})
	except Exception as e: 
		return e

	# try:
	# 	#bitfinex_price() +
	# 	cr_value = coinbase_price(currency='USD') + '\n'+ quadrigacx_price(fiatCurrency='usd',
	# 		cryptoCurrency='btc') + '\n\n' + coinbase_price(currency='CAD') + '\n'+ quadrigacx_price('cad','btc')
	# 	print cr_value
	# except Exception as e:
	# 	print('Error::: {}'.format(e))
	# return cr_value



################################
#
# Prodcution URLs For LoonieCoin Project 
#
################################



@app.route('/phoneProvince/{mobileNumber}')
def phone_province(mobileNumber):
	verPhone = PhoneValidator(mobileNumber)
	return verPhone.phoneProvince()



 # The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
@app.route('/verphone/{mobileNumber}')
def mobile_verifer(mobileNumber):
	verPhone = PhoneValidator(mobileNumber)
	return verPhone.mobileVerifer()