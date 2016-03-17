# Валютный своп

## SwapDynamic(FromDate, ToDate)  Условия заключения сделок «валютный своп» по покупке долларов США и евро за рубли, заключенных Банком России XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [Swap], 
таблица содержит поля:

DateBuy Дата начала сделки
DateSell Дата окончания сделки
BaseRate Процентная ставка по российским рублям, в процентах годовых, %
SD Базовый курс, руб./долл.
TIR Своп-разница, руб.
DEADLINEBS Время завершения расчетов в первый день сделки

## SwapDayTotal (FromDate, ToDate) Задолженность кредитных организаций перед Банком России по сделкам «валютный своп» XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## SwapMonthTotal (FromDate, ToDate) Объем сделок «валютный своп» по покупке долларов сша и евро за рубли, заключенных банком россии XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## SwapInfoSellUSD (FromDate, ToDate) Условия заключения сделок «валютный своп» по продаже долларов сша за рубли XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## SwapInfoSellUSDVol (FromDate, ToDate) Объем сделок «валютный своп» по продаже долларов сша за рубли, заключенных банком россии XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## RepoDebtUSD (FromDate, ToDate) Задолженность кредитных организаций перед Банком России по операциям РЕПО в иностранной валюте RepoDebtUSD.xsd new
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Данные методы возвращают только 'простые' XML документы, без использования схем:




# Монеты и драгметаллы

## Coins_base (FromDate, ToDate) Отпускные цены Банка России на инвестиционные монеты XSD
Аргументы: 

FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
## FixingBase (FromDate, ToDate) Фиксинги на драгоценные металлы XSD
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime

## DragMetDynamic(FromDate, ToDate) Получение динамики учетных цен на драгоценные металлы
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [DrgMet], 
таблица содержит поля:

DateMet Дата котирования
CodMet Тип металла (1- Золото, 2- Серебро,3 -Платина,4 - Палладий)
price Учетная цена
ВНИМАНИЕ c 01.07.2008 дата установления цены является действующей, до 01.07.2008 - датой установления.

##NewsInfo(FromDate, ToDate) Получение новостей сервера 
Аргументы: 
FromDate Дата начала, тип System.DateTime
ToDate Дата окончания, тип System.DateTime
Результат:
XML документ в формате System.Data.Dataset, содержащий таблицу [News], 
таблица содержит поля:

Doc_id ID документа
DocDate Дата документа
Title Заголовок
Url URL документа


# XML методы 

## Updated MainInfoXML() Получение основной информации - Ставка рефинансирования, золотовалютные резервы, денежная база, денежная масса
## XVolXML() Операции Банка России на рынке государственных ценных бумаг по поручению Министерства финансов Российской Федерации
## OmodInfoXML() Операции на открытом рынке
## AllDataInfoXML() Получение всей оперативной (ежедневной) информации
Метода для работы с базой по курсам редких валют, предоставляемые агентством «Thomson Reuters» new

## GetLatestReutersDateTime Последняя дата публикации редких валют от Thomson Reuters
## EnumReutersValutes Справочник по кодам редких валют от Thomson Reuters
## GetReutersCursOnDate Получение ежедневных курсов редких валют от Thomson Reuters
## GetReutersCursDynamic Получение динамики ежедневных курсов редкой валюты от Thomson Reuters
