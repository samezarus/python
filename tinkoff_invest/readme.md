Проект для Тинькофф инвестиций

Да. Да. Есть неофициальный API (python) но вот мануалов для него я не нашёл. 

	Вру, нашёл https://tinkoffcreditsystems.github.io/invest-openapi/swagger-ui/#/market/get_market_candles

Разбираться - это не мой путь. За основу возьму исходники на GO, т.к. они более лаконичные https://github.com/TinkoffCreditSystems/invest-openapi-go-sdk

Собственно всё сводится к простой отправке GET-запросов, и получения на них JSON-ответов.

Песочницу рассматривать не буду. Сразу в бой.

apiURL = 'https://api-invest.tinkoff.ru/openapi'

figi - айдишник инструмента(акции/облигации) в системе (список доступных можно получить через '/market/stocks')

(figi: COCA-COLA: BBG000BMX289)

ticker - краткое наименование инструиента

Portfolio

	apiURL + '/portfolio'
	
	apiURL + '/portfolio/currencies'

Market

	apiURL + '/market'
	
	apiURL + '/market/bonds'
	
	apiURL + '/market/currencies'
	
	apiURL + '/market/etfs'
	
	apiURL + '/market/stocks' - доступные инструменты
	
	apiURL + '/market/search/by-figi?figi=' + figi - поиск инструмента
	
	apiURL + '/market/search/by-ticker?ticker=' + ticker - поиск инструмента
	
	apiURL + '/market/candles?' + q.Encode() - свечи
	
	apiURL + '/market/orderbook?' + q.Encode()
	
Orders

	apiURL + '/orders'
	
	apiURL + '/orders/cancel?orderId=' + id
	
	apiURL + '/orders/limit-order?figi=' + figi
	
	
Operations

	apiURL + '/operations' + q.Encode()


зы: Кому интересно и есть идеи, пишите в телегу https://t.me/sameza
