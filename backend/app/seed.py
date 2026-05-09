from app.database import SessionLocal
from app.models import Holiday, WorkDay
import json

INITIAL_HOLIDAYS = [
    {
        "name": "День заповедников и национальных парков",
        "day": 11, "month": 0, "type": "eco", "region": "russia",
        "description": "Праздник, посвященный сохранению уникальных природных территорий России.",
        "events": ["Экскурсии в заповедники", "Экологические лекции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_заповедников"
    },
    {
        "name": "Всемирный день мокрых земель",
        "day": 2, "month": 1, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению и разумному использованию болот и водно-болотных угодий.",
        "events": ["Экскурсии на болота", "Лекции о значении водно-болотных угодий"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_мокрых_земель"
    },
    {
        "name": "Международный день дикой природы",
        "day": 3, "month": 2, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению дикой природы и биоразнообразия планеты.",
        "events": ["Фотосессии дикой природы", "Акции по защите животных"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_дикой_природы"
    },
    {
        "name": "Всемирный день водных ресурсов",
        "day": 22, "month": 2, "type": "eco", "region": "world",
        "description": "День, напоминающий о важности пресной воды для жизни на Земле.",
        "events": ["Конференции по очистке воды", "Школьные уроки о водных ресурсах"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_водных_ресурсов"
    },
    {
        "name": "Всемирный день леса",
        "day": 21, "month": 2, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению и защите лесов по всему миру.",
        "events": ["Массовые посадки деревьев", "Лесные экскурсии"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_леса"
    },
    {
        "name": "Всемирный день здоровья",
        "day": 7, "month": 3, "type": "eco", "region": "world",
        "description": "День, подчеркивающий важность здорового образа жизни и чистой окружающей среды.",
        "events": ["Марафоны и пробежки", "Лекции о здоровом питании"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_здоровья"
    },
    {
        "name": "День Земли",
        "day": 22, "month": 3, "type": "eco", "region": "world",
        "description": "Глобальное событие, направленное на защиту окружающей среды и повышение экологической осведомленности.",
        "events": ["Посадка деревьев", "Уборка мусора", "Экологические акции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_Земли"
    },
    {
        "name": "Международный день птиц",
        "day": 1, "month": 3, "type": "eco", "region": "world",
        "description": "День, посвященный защите птиц и их мест обитания.",
        "events": ["Наблюдение за птицами", "Создание кормушек", "Лекции о перелетных птицах"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_птиц"
    },
    {
        "name": "День работника лесного хозяйства",
        "day": 3, "month": 9, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников лесной промышленности и лесного хозяйства.",
        "events": ["Профессиональные конкурсы", "Лесные фестивали"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_работника_лесного_хозяйства"
    },
    {
        "name": "День эколога",
        "day": 5, "month": 5, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник экологов и специалистов по охране природы.",
        "events": ["Экологические конференции", "Природоохранные акции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_эколога"
    },
    {
        "name": "Всемирный день окружающей среды",
        "day": 5, "month": 5, "type": "eco", "region": "world",
        "description": "Главный праздник ООН для привлечения внимания к проблемам окружающей среды.",
        "events": ["Экологические форумы", "Акции по переработке", "Зеленые митинги"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_окружающей_среды"
    },
    {
        "name": "Всемирный день борьбы с опустыниванием и засухой",
        "day": 17, "month": 5, "type": "eco", "region": "world",
        "description": "День, посвященный проблемам опустынивания земель и засухи.",
        "events": ["Лекции о опустынивании", "Акции по сохранению почв"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_борьбы_с_опустыниванием_и_засухой"
    },
    {
        "name": "Всемирный день океанов",
        "day": 8, "month": 5, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению океанов и морских ресурсов.",
        "events": ["Пляжные уборки", "Лекции о морской экологии", "Фестивали океана"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_океанов"
    },
    {
        "name": "День работника рыбного хозяйства",
        "day": 9, "month": 6, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников рыбной промышленности.",
        "events": ["Рыболовные соревнования", "Дегустации рыбы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_работника_рыбного_хозяйства"
    },
    {
        "name": "Международный день сохранения mangrove экосистем",
        "day": 26, "month": 6, "type": "eco", "region": "world",
        "description": "День, посвященный защите мангровых лесов и прибрежных экосистем.",
        "events": ["Посадка мангровых деревьев", "Лекции о прибрежных экосистемах"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_сохранения_mangrove_экосистем"
    },
    {
        "name": "Всемирный день популяций",
        "day": 11, "month": 6, "type": "eco", "region": "world",
        "description": "День, посвященный проблемам перенаселения и устойчивого развития.",
        "events": ["Конференции по демографии", "Лекции о планировании семьи"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_населения"
    },
    {
        "name": "День ветерана и пенсионера лесного хозяйства",
        "day": 16, "month": 7, "type": "eco", "region": "russia",
        "description": "День памяти и уважения к ветеранам лесной отрасли.",
        "events": ["Встречи с ветеранами", "Лесные прогулки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Лесное_хозяйство_России"
    },
    {
        "name": "Международный день коренных народов мира",
        "day": 9, "month": 7, "type": "eco", "region": "world",
        "description": "День, посвященный защите прав и культур коренных народов, сохраняющих традиционные знания о природе.",
        "events": ["Фестивали коренных культур", "Лекции о традиционных знаниях"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_коренных_народов_мира"
    },
    {
        "name": "Всемирный день защиты животных",
        "day": 4, "month": 9, "type": "eco", "region": "world",
        "description": "День, посвященный защите животных от жестокости и сохранению биоразнообразия.",
        "events": ["Акции по защите животных", "Дни открытых дверей в приютах"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_защиты_животных"
    },
    {
        "name": "Всемирный день чистого воздуха для голубого неба",
        "day": 7, "month": 8, "type": "eco", "region": "world",
        "description": "День, посвященный проблемам загрязнения воздуха и климатическим изменениям.",
        "events": ["Мониторинг качества воздуха", "Акции по снижению выбросов"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Загрязнение_атмосферы"
    },
    {
        "name": "Международный день сохранения озонового слоя",
        "day": 16, "month": 8, "type": "eco", "region": "world",
        "description": "День, посвященный защите озонового слоя Земли.",
        "events": ["Лекции об озоновом слое", "Акции по защите климата"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_охраны_озонового_слоя"
    },
    {
        "name": "Всемирный день гор",
        "day": 11, "month": 11, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению горных экосистем и устойчивому развитию горных регионов.",
        "events": ["Горные походы", "Лекции о горной экологии"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_гор"
    },
    {
        "name": "День работника охотничьего и рыболовного хозяйства",
        "day": 26, "month": 11, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников охотничьего и рыбного хозяйства.",
        "events": ["Охотничьи соревнования", "Рыболовные фестивали"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Охотничье_хозяйство_России"
    },
    {
        "name": "Всемирный день почвы",
        "day": 5, "month": 11, "type": "eco", "region": "world",
        "description": "День, посвященный сохранению почв и устойчивому земледелию.",
        "events": ["Лекции о почвоведении", "Акции по защите почв"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_почвы"
    },
    {
        "name": "День России",
        "day": 12, "month": 5, "type": "national", "region": "russia",
        "description": "Государственный праздник Российской Федерации.",
        "events": ["Праздничные концерты", "Салюты"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_России"
    },
    {
        "name": "День работника сельского хозяйства и перерабатывающей промышленности",
        "day": 9, "month": 9, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников агропромышленного комплекса.",
        "events": ["Аграрные выставки", "Фермерские ярмарки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Сельское_хозяйство_России"
    },
    {
        "name": "День работника гидрометеорологической службы России",
        "day": 23, "month": 2, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник метеорологов и гидрологов.",
        "events": ["Дни открытых дверей в метеоцентрах", "Лекции о погоде"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Гидрометцентр_России"
    },
    {
        "name": "День работника государственной инспекции по охране природы",
        "day": 24, "month": 4, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников природоохраны.",
        "events": ["Экологические рейды", "Лекции о природоохранной деятельности"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Росприроднадзор"
    },
    {
        "name": "День работника заповедного дела",
        "day": 14, "month": 7, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников заповедников и национальных парков.",
        "events": ["Экскурсии в заповедники", "Конференции по охране природы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Особо_охраняемые_природные_территории_России"
    },
    {
        "name": "День работника геологической службы",
        "day": 31, "month": 3, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник геологов и работников геологической службы.",
        "events": ["Геологические экскурсии", "Выставки минералов"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Геологическая_служба_России"
    },
    {
        "name": "День работника водного хозяйства",
        "day": 5, "month": 5, "type": "eco", "region": "russia",
        "description": "Профессиональный праздник работников водного хозяйства.",
        "events": ["Экскурсии на водные объекты", "Лекции о водных ресурсах"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Водное_хозяйство_России"
    },
    # Международные праздники
    {
        "name": "Новый год",
        "day": 1, "month": 0, "type": "world", "region": "world",
        "description": "Международный праздник, отмечаемый во многих странах мира.",
        "events": ["Новогодние ёлки", "Фейерверки", "Праздничные ужины"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Новый_год"
    },
    {
        "name": "Международный женский день",
        "day": 8, "month": 2, "type": "world", "region": "world",
        "description": "День, посвященный правам женщин и достижению гендерного равенства.",
        "events": ["Поздравления женщин", "Феминистские акции", "Цветочные подарки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_женский_день"
    },
    {
        "name": "Международный день труда",
        "day": 1, "month": 4, "type": "world", "region": "world",
        "description": "День солидарности трудящихся всего мира.",
        "events": ["Профсоюзные митинги", "Праздничные шествия", "Демонстрации"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_труда"
    },
    {
        "name": "День победы",
        "day": 9, "month": 4, "type": "world", "region": "world",
        "description": "День победы над фашизмом во Второй мировой войне.",
        "events": ["Военные парады", "Ветеранские встречи", "Праздничные салюты"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_Победы"
    },
    {
        "name": "Международный день детей",
        "day": 1, "month": 5, "type": "world", "region": "world",
        "description": "День, посвященный защите прав и благополучия детей.",
        "events": ["Детские праздники", "Акции помощи детям", "Школьные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_защиты_детей"
    },
    {
        "name": "Международный день молодежи",
        "day": 12, "month": 7, "type": "world", "region": "world",
        "description": "День, посвященный молодежи и ее роли в обществе.",
        "events": ["Молодежные фестивали", "Спортивные соревнования", "Форумы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_молодёжи"
    },
    {
        "name": "Международный день грамотности",
        "day": 8, "month": 8, "type": "world", "region": "world",
        "description": "День, посвященный проблемам неграмотности в мире.",
        "events": ["Книжные ярмарки", "Лекции о грамотности", "Акции по обучению"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_грамотности"
    },
    {
        "name": "Международный день мира",
        "day": 21, "month": 8, "type": "world", "region": "world",
        "description": "День, посвященный укреплению мира во всем мире.",
        "events": ["Мирные демонстрации", "Форумы о мире", "Культурные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_мира"
    },
    {
        "name": "Международный день пожилых людей",
        "day": 1, "month": 9, "type": "world", "region": "world",
        "description": "День, посвященный проблемам пожилых людей и их вкладу в общество.",
        "events": ["Концерты для пенсионеров", "Лекции о старении", "Акции помощи"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_пожилых_людей"
    },
    {
        "name": "Международный день учителя",
        "day": 5, "month": 9, "type": "world", "region": "world",
        "description": "День, посвященный учителям и их важной роли в образовании.",
        "events": ["Поздравления учителей", "Школьные концерты", "Педагогические конференции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Всемирный_день_учителя"
    },
    {
        "name": "Международный день прав человека",
        "day": 10, "month": 11, "type": "world", "region": "world",
        "description": "День, посвященный Всеобщей декларации прав человека.",
        "events": ["Лекции о правах человека", "Правозащитные акции", "Культурные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Международный_день_прав_человека"
    },
    {
        "name": "Рождество Христово",
        "day": 25, "month": 11, "type": "world", "region": "world",
        "description": "Главный христианский праздник, отмечаемый во многих странах.",
        "events": ["Рождественские службы", "Подарки", "Семейные ужины"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Рождество_Христово"
    },
    # Российские праздники
    {
        "name": "Рождество Христово (православное)",
        "day": 7, "month": 0, "type": "national", "region": "russia",
        "description": "Главный православный праздник в России.",
        "events": ["Рождественские богослужения", "Праздничные ужины", "Рождественские подарки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Рождество_Христово_(православие)"
    },
    {
        "name": "День защитника Отечества",
        "day": 23, "month": 1, "type": "national", "region": "russia",
        "description": "День воинской славы России, посвященный защитникам Родины.",
        "events": ["Военные парады", "Поздравления ветеранов", "Патриотические мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_защитника_Отечества"
    },
    {
        "name": "Масленица",
        "day": 24, "month": 1, "type": "national", "region": "russia",
        "description": "Народный славянский праздник проводов зимы.",
        "events": ["Блины", "Сжигание чучела", "Народные гуляния"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Масленица"
    },
    {
        "name": "День космонавтики",
        "day": 12, "month": 3, "type": "national", "region": "russia",
        "description": "День первого полета человека в космос.",
        "events": ["Космические выставки", "Лекции о космосе", "Научные форумы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_космонавтики"
    },
    {
        "name": "Пасха",
        "day": 5, "month": 4, "type": "national", "region": "russia",
        "description": "Главный православный праздник Воскресения Христова.",
        "events": ["Пасхальные богослужения", "Крашение яиц", "Пасхальные куличи"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Пасха"
    },
    {
        "name": "День славянской письменности и культуры",
        "day": 24, "month": 4, "type": "national", "region": "russia",
        "description": "День, посвященный создателям славянской азбуки Кириллу и Мефодию.",
        "events": ["Литературные вечера", "Концерты", "Книжные ярмарки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_славянской_письменности_и_культуры"
    },
    {
        "name": "День России",
        "day": 12, "month": 5, "type": "national", "region": "russia",
        "description": "Государственный праздник Российской Федерации.",
        "events": ["Праздничные концерты", "Салюты", "Патриотические мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_России"
    },
    {
        "name": "День семьи, любви и верности",
        "day": 8, "month": 6, "type": "national", "region": "russia",
        "description": "День, посвященный семейным ценностям и православным святым Петру и Февронии.",
        "events": ["Семейные праздники", "Свадебные церемонии", "Концерты"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_семьи,_любви_и_верности"
    },
    {
        "name": "День военно-морского флота",
        "day": 31, "month": 6, "type": "national", "region": "russia",
        "description": "День, посвященный военно-морскому флоту России.",
        "events": ["Парады кораблей", "Морские фестивали", "Военные демонстрации"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_Военно-Морского_Флота"
    },
    {
        "name": "День физкультурника",
        "day": 12, "month": 7, "type": "national", "region": "russia",
        "description": "День, посвященный спорту и физической культуре.",
        "events": ["Спортивные соревнования", "Физкультурные парады", "Оздоровительные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_физкультурника"
    },
    {
        "name": "День воздушно-десантных войск",
        "day": 2, "month": 7, "type": "national", "region": "russia",
        "description": "День, посвященный ВДВ России.",
        "events": ["Военные парады", "Праздничные концерты", "Десантные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_Воздушно-десантных_войск"
    },
    {
        "name": "День строителя",
        "day": 12, "month": 7, "type": "national", "region": "russia",
        "description": "Профессиональный праздник строителей.",
        "events": ["Строительные выставки", "Архитектурные экскурсии", "Профессиональные конкурсы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_строителя"
    },
    {
        "name": "День железнодорожника",
        "day": 31, "month": 7, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников железнодорожного транспорта.",
        "events": ["Железнодорожные выставки", "Экскурсии на вокзалы", "Профессиональные конкурсы"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_железнодорожника"
    },
    {
        "name": "День шахтера",
        "day": 26, "month": 7, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников горнодобывающей промышленности.",
        "events": ["Шахтерские фестивали", "Профессиональные конкурсы", "Памятные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_шахтёра"
    },
    {
        "name": "День пограничника",
        "day": 28, "month": 7, "type": "national", "region": "russia",
        "description": "День, посвященный пограничным войскам России.",
        "events": ["Пограничные парады", "Военные демонстрации", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_пограничника"
    },
    {
        "name": "День Воздушных сил России",
        "day": 12, "month": 7, "type": "national", "region": "russia",
        "description": "День, посвященный военно-воздушным силам России.",
        "events": ["Авиационные шоу", "Военные парады", "Аэрокосмические выставки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_Воздушных_сил_России"
    },
    {
        "name": "День ВМФ России",
        "day": 9, "month": 6, "type": "national", "region": "russia",
        "description": "День, посвященный военно-морскому флоту России.",
        "events": ["Морские парады", "Военные демонстрации", "Флотские праздники"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Военно-морской_флот_России"
    },
    {
        "name": "День сотрудника органов внутренних дел",
        "day": 10, "month": 10, "type": "national", "region": "russia",
        "description": "День, посвященный сотрудникам полиции и МВД России.",
        "events": ["Полицейские парады", "Профессиональные мероприятия", "Памятные акции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_сотрудника_органов_внутренних_дел_Российской_Федерации"
    },
    {
        "name": "День народного единства",
        "day": 4, "month": 10, "type": "national", "region": "russia",
        "description": "Государственный праздник России, посвященный освобождению Москвы от польских интервентов.",
        "events": ["Патриотические мероприятия", "Исторические лекции", "Культурные фестивали"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_народного_единства"
    },
    {
        "name": "День матери",
        "day": 28, "month": 10, "type": "national", "region": "russia",
        "description": "День, посвященный матерям и материнству.",
        "events": ["Семейные праздники", "Концерты", "Поздравления матерей"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_матери_(Россия)"
    },
    {
        "name": "День бухгалтера",
        "day": 6, "month": 10, "type": "national", "region": "russia",
        "description": "Профессиональный праздник бухгалтеров и экономистов.",
        "events": ["Профессиональные семинары", "Финансовые конференции", "Корпоративные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Бухгалтерский_учёт"
    },
    {
        "name": "День ракетных войск и артиллерии",
        "day": 19, "month": 10, "type": "national", "region": "russia",
        "description": "День, посвященный ракетным войскам и артиллерии России.",
        "events": ["Военные демонстрации", "Артиллерийские парады", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_ракетных_войск_и_артиллерии"
    },
    {
        "name": "День таможенника",
        "day": 25, "month": 10, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников таможенной службы.",
        "events": ["Таможенные выставки", "Профессиональные конкурсы", "Корпоративные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Таможенная_служба_России"
    },
    {
        "name": "День юриста",
        "day": 3, "month": 11, "type": "national", "region": "russia",
        "description": "Профессиональный праздник юристов и работников правовой системы.",
        "events": ["Юридические конференции", "Правовые лекции", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_юриста"
    },
    {
        "name": "День ГИБДД",
        "day": 3, "month": 6, "type": "national", "region": "russia",
        "description": "День, посвященный сотрудникам Государственной инспекции безопасности дорожного движения.",
        "events": ["Автошоу", "Безопасные гонки", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/ГИБДД"
    },
    {
        "name": "День работника культуры",
        "day": 25, "month": 2, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников культуры и искусства.",
        "events": ["Культурные фестивали", "Концерты", "Выставки"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_работника_культуры"
    },
    {
        "name": "День учителя",
        "day": 5, "month": 9, "type": "national", "region": "russia",
        "description": "Профессиональный праздник учителей и работников образования.",
        "events": ["Школьные концерты", "Педагогические конференции", "Поздравления учителей"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_учителя_(Россия)"
    },
    {
        "name": "День медицинского работника",
        "day": 3, "month": 9, "type": "national", "region": "russia",
        "description": "Профессиональный праздник врачей и медицинских работников.",
        "events": ["Медицинские конференции", "Дни открытых дверей в больницах", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/День_медицинского_работника"
    },
    {
        "name": "День работника торговли",
        "day": 25, "month": 6, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников торговли и общественного питания.",
        "events": ["Торговые ярмарки", "Профессиональные конкурсы", "Корпоративные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Торговля_в_России"
    },
    {
        "name": "День работника связи",
        "day": 7, "month": 4, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников связи и телекоммуникаций.",
        "events": ["Технологические выставки", "Конференции по связи", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Связь_в_России"
    },
    {
        "name": "День работника транспорта",
        "day": 9, "month": 5, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников транспортной отрасли.",
        "events": ["Транспортные выставки", "Профессиональные конкурсы", "Автошоу"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Транспорт_в_России"
    },
    {
        "name": "День химика",
        "day": 26, "month": 4, "type": "national", "region": "russia",
        "description": "Профессиональный праздник химиков и работников химической промышленности.",
        "events": ["Химические выставки", "Научные лекции", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Химическая_промышленность_России"
    },
    {
        "name": "День энергетика",
        "day": 22, "month": 11, "type": "national", "region": "russia",
        "description": "Профессиональный праздник работников энергетической отрасли.",
        "events": ["Энергетические выставки", "Технологические конференции", "Профессиональные мероприятия"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Энергетика_России"
    },
    {
        "name": "День государственного флага Российской Федерации",
        "day": 22, "month": 7, "type": "national", "region": "russia",
        "description": "День, посвященный государственному флагу России.",
        "events": ["Патриотические мероприятия", "Флаговые церемонии", "Культурные фестивали"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Флаг_России"
    },
    {
        "name": "День конституции Российской Федерации",
        "day": 12, "month": 11, "type": "national", "region": "russia",
        "description": "День принятия Конституции Российской Федерации.",
        "events": ["Юридические лекции", "Конституционные мероприятия", "Патриотические акции"],
        "wikipedia_url": "https://ru.wikipedia.org/wiki/Конституция_Российской_Федерации"
    }
]

# Производственный календарь 2026 года (РФ)
# 0 - рабочий день, 1 - выходной день, 2 - праздничный день
WORK_DAYS_2026 = [
    # Январь 2026 (15 рабочих, 8 выходных, 8 праздников)
    # Новогодние каникулы: 31 декабря 2025 - 11 января 2026
    {"day": 1, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Новый год
    {"day": 2, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Новый год
    {"day": 3, "month": 0, "year": 2026, "is_weekend": 0, "is_holiday": 0},  # Суббота, перенесено на 9 января
    {"day": 4, "month": 0, "year": 2026, "is_weekend": 0, "is_holiday": 0},  # Воскресенье, перенесено на 31 декабря
    {"day": 5, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Новый год
    {"day": 6, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Новый год
    {"day": 7, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Рождество Христово
    {"day": 8, "month": 0, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Новый год
    {"day": 9, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Выходной за 3 января
    {"day": 10, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 11, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 17, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 18, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 24, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 25, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 31, "month": 0, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота

    # Февраль 2026 (19 рабочих, 8 выходных, 1 праздник)
    {"day": 7, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 8, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 14, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 15, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 21, "month": 1, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # День защитника Отечества
    {"day": 22, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Выходной за 21 февраля
    {"day": 23, "month": 1, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # День защитника Отечества
    {"day": 28, "month": 1, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота

    # Март 2026 (21 рабочий, 9 выходных, 1 праздник)
    {"day": 1, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 7, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 8, "month": 2, "year": 2026, "is_weekend": 2, "is_holiday": 1},  # Международный женский день
    {"day": 9, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Выходной за 8 марта
    {"day": 14, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 15, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 21, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 22, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 28, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 29, "month": 2, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    
    # Апрель 2026 (22 рабочих, 8 выходных)
    {"day": 4, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 5, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 11, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 12, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 18, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 19, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    {"day": 25, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Суббота
    {"day": 26, "month": 3, "year": 2026, "is_weekend": 1, "is_holiday": 0},  # Воскресенье
    
    # Май 2026
    # 1 мая - Пятница (Праздник Весны и Труда)
    {"day": 1, "month": 4, "year": 2026, "is_weekend": 2, "is_holiday": 1},
    # 2 мая - Суббота (Выходной)
    {"day": 2, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 3 мая - Воскресенье (Выходной)
    {"day": 3, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 8 мая - Пятница (Выходной за 1 мая)
    {"day": 8, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 9 мая - Суббота (День Победы)
    {"day": 9, "month": 4, "year": 2026, "is_weekend": 2, "is_holiday": 1},
    # 10 мая - Воскресенье (Выходной)
    {"day": 10, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 11 мая - Понедельник (Выходной за 9 мая)
    {"day": 11, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 16 мая - Суббота (Выходной)
    {"day": 16, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 17 мая - Воскресенье (Выходной)
    {"day": 17, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 23 мая - Суббота (Выходной)
    {"day": 23, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 24 мая - Воскресенье (Выходной)
    {"day": 24, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 30 мая - Суббота (Выходной)
    {"day": 30, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 31 мая - Воскресенье (Выходной)
    {"day": 31, "month": 4, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Июнь 2026
    # 6 июня - Суббота (Выходной)
    {"day": 6, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 7 июня - Воскресенье (Выходной)
    {"day": 7, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 12 июня - Пятница (День России)
    {"day": 12, "month": 5, "year": 2026, "is_weekend": 2, "is_holiday": 1},
    # 13 июня - Суббота (Выходной)
    {"day": 13, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 14 июня - Воскресенье (Выходной)
    {"day": 14, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 20 июня - Суббота (Выходной)
    {"day": 20, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 21 июня - Воскресенье (Выходной)
    {"day": 21, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 27 июня - Суббота (Выходной)
    {"day": 27, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 28 июня - Воскресенье (Выходной)
    {"day": 28, "month": 5, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Июль 2026
    # 4 июля - Суббота (Выходной)
    {"day": 4, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 5 июля - Воскресенье (Выходной)
    {"day": 5, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 11 июля - Суббота (Выходной)
    {"day": 11, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 12 июля - Воскресенье (Выходной)
    {"day": 12, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 18 июля - Суббота (Выходной)
    {"day": 18, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 19 июля - Воскресенье (Выходной)
    {"day": 19, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 25 июля - Суббота (Выходной)
    {"day": 25, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 26 июля - Воскресенье (Выходной)
    {"day": 26, "month": 6, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Август 2026
    # 1 августа - Суббота (Выходной)
    {"day": 1, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 2 августа - Воскресенье (Выходной)
    {"day": 2, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 8 августа - Суббота (Выходной)
    {"day": 8, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 9 августа - Воскресенье (Выходной)
    {"day": 9, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 15 августа - Суббота (Выходной)
    {"day": 15, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 16 августа - Воскресенье (Выходной)
    {"day": 16, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 22 августа - Суббота (Выходной)
    {"day": 22, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 23 августа - Воскресенье (Выходной)
    {"day": 23, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 29 августа - Суббота (Выходной)
    {"day": 29, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 30 августа - Воскресенье (Выходной)
    {"day": 30, "month": 7, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Сентябрь 2026
    # 5 сентября - Суббота (Выходной)
    {"day": 5, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 6 сентября - Воскресенье (Выходной)
    {"day": 6, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 12 сентября - Суббота (Выходной)
    {"day": 12, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 13 сентября - Воскресенье (Выходной)
    {"day": 13, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 19 сентября - Суббота (Выходной)
    {"day": 19, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 20 сентября - Воскресенье (Выходной)
    {"day": 20, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 26 сентября - Суббота (Выходной)
    {"day": 26, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 27 сентября - Воскресенье (Выходной)
    {"day": 27, "month": 8, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Октябрь 2026
    # 3 октября - Суббота (Выходной)
    {"day": 3, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 4 октября - Воскресенье (Выходной)
    {"day": 4, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 10 октября - Суббота (Выходной)
    {"day": 10, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 11 октября - Воскресенье (Выходной)
    {"day": 11, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 17 октября - Суббота (Выходной)
    {"day": 17, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 18 октября - Воскресенье (Выходной)
    {"day": 18, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 24 октября - Суббота (Выходной)
    {"day": 24, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 25 октября - Воскресенье (Выходной)
    {"day": 25, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 31 октября - Суббота (Выходной)
    {"day": 31, "month": 9, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Ноябрь 2026
    # 1 ноября - Воскресенье (Выходной)
    {"day": 1, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 4 ноября - Среда (День народного единства)
    {"day": 4, "month": 10, "year": 2026, "is_weekend": 2, "is_holiday": 1},
    # 5 ноября - Четверг (Выходной за 4 ноября)
    {"day": 5, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 7 ноября - Суббота (Выходной)
    {"day": 7, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 8 ноября - Воскресенье (Выходной)
    {"day": 8, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 14 ноября - Суббота (Выходной)
    {"day": 14, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 15 ноября - Воскресенье (Выходной)
    {"day": 15, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 21 ноября - Суббота (Выходной)
    {"day": 21, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 22 ноября - Воскресенье (Выходной)
    {"day": 22, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 28 ноября - Суббота (Выходной)
    {"day": 28, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 29 ноября - Воскресенье (Выходной)
    {"day": 29, "month": 10, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    
    # Декабрь 2026
    # 5 декабря - Суббота (Выходной)
    {"day": 5, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 6 декабря - Воскресенье (Выходной)
    {"day": 6, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 12 декабря - Суббота (Выходной)
    {"day": 12, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 13 декабря - Воскресенье (Выходной)
    {"day": 13, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 19 декабря - Суббота (Выходной)
    {"day": 19, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 20 декабря - Воскресенье (Выходной)
    {"day": 20, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 26 декабря - Суббота (Выходной)
    {"day": 26, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 27 декабря - Воскресенье (Выходной)
    {"day": 27, "month": 11, "year": 2026, "is_weekend": 1, "is_holiday": 0},
    # 31 декабря - Четверг (Праздник)
    {"day": 31, "month": 11, "year": 2026, "is_weekend": 2, "is_holiday": 1},
]

def seed_database():
    db = SessionLocal()
    try:
        # Добавляем праздники
        if db.query(Holiday).count() == 0:
            for holiday_data in INITIAL_HOLIDAYS:
                holiday = Holiday(
                    **{k: v for k, v in holiday_data.items() if k != 'events'},
                    events=json.dumps(holiday_data.get('events', []))
                )
                db.add(holiday)
            db.commit()
        
        # Добавляем производственный календарь
        if db.query(WorkDay).count() == 0:
            for work_day_data in WORK_CALENDAR_2026:
                work_day = WorkDay(**work_day_data)
                db.add(work_day)
            db.commit()
    finally:
        db.close()