import asyncio
import logging
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.geography import City
from app.core.maps import GoogleMapsClient
from app.services.poi import POIService  # Импортируем Сервис, а не Репозиторий

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Твой список RAW_POIS с русскими названиями городов
RAW_POIS = [
    # --- КИТАЙ ---
    # Фошань
    {"city_name": "Фошань", "name": "Ancestral Temple (Zumiao)", "desc": "Главный храм города и музей кунг-фу.", "indoor": False},
    {"city_name": "Фошань", "name": "Nanfeng Ancient Kiln", "desc": "Древние печи для обжига керамики.", "indoor": False},
    {"city_name": "Фошань", "name": "Liang's Garden", "desc": "Классический кантонский сад.", "indoor": False},
    {"city_name": "Фошань", "name": "Xiqiao Mountain", "desc": "Священная гора со статуей богини Гуаньинь.", "indoor": False},
    {"city_name": "Фошань", "name": "Wong Fei-hung Memorial Hall", "desc": "Музей легендарного мастера боевых искусств.", "indoor": True},
    {"city_name": "Фошань", "name": "Shunde Qinghui Garden", "desc": "Один из четырех великих садов провинции.", "indoor": False},
    {"city_name": "Фошань", "name": "Florence Village", "desc": "Премиальный аутлет в итальянском стиле.", "indoor": True},
    {"city_name": "Фошань", "name": "Bruce Lee Ancestral House", "desc": "Дом предков Брюса Ли.", "indoor": True},
    {"city_name": "Фошань", "name": "Sanshui Lotus World", "desc": "Огромный парк лотосов.", "indoor": False},
    {"city_name": "Фошань", "name": "Lingnan Tiandi", "desc": "Исторический район с кафе и магазинами.", "indoor": False},

    # Гуанчжоу
    {"city_name": "Гуанчжоу", "name": "Canton Tower", "desc": "Телебашня с панорамным видом.", "indoor": True},
    {"city_name": "Гуанчжоу", "name": "Chen Clan Ancestral Hall", "desc": "Шедевр кантонской архитектуры.", "indoor": True},
    {"city_name": "Гуанчжоу", "name": "Yuexiu Park", "desc": "Крупнейший парк с символом города — Пятью Овнами.", "indoor": False},
    {"city_name": "Гуанчжоу", "name": "Shamian Island", "desc": "Остров с европейской колониальной архитектурой.", "indoor": False},
    {"city_name": "Гуанчжоу", "name": "Baiyun Mountain", "desc": "Живописная гора 'Белых облаков'.", "indoor": False},
    {"city_name": "Гуанчжоу", "name": "Sacred Heart Cathedral", "desc": "Величественный готический собор.", "indoor": True},
    {"city_name": "Гуанчжоу", "name": "Chimelong Safari Park", "desc": "Один из лучших зоопарков мира.", "indoor": False},
    {"city_name": "Гуанчжоу", "name": "Baima Garment Market", "desc": "Огромный рынок одежды.", "indoor": True},
    {"city_name": "Гуанчжоу", "name": "Pearl River Night Cruise", "desc": "Ночной круиз по реке Чжуцзян.", "indoor": False},
    {"city_name": "Гуанчжоу", "name": "Museum of the Mausoleum of the Nanyue King", "desc": "Древняя гробница и музей.", "indoor": True},

    # Шэньчжэнь
    {"city_name": "Шэньчжэнь", "name": "Window of the World", "desc": "Парк с миниатюрами мировых достопримечательностей.", "indoor": False},
    {"city_name": "Шэньчжэнь", "name": "Splendid China Folk Village", "desc": "Этнографический парк культур Китая.", "indoor": False},
    {"city_name": "Шэньчжэнь", "name": "Ping An Finance Centre", "desc": "Один из самых высоких небоскребов мира.", "indoor": True},
    {"city_name": "Шэньчжэнь", "name": "OCT-LOFT Creative Culture Park", "desc": "Арт-кластер в бывшей промзоне.", "indoor": False},
    {"city_name": "Шэньчжэнь", "name": "Fairy Lake Botanical Garden", "desc": "Ботанический сад и буддийский храм.", "indoor": False},
    {"city_name": "Шэньчжэнь", "name": "Huaqiangbei Electronics Market", "desc": "Легендарный рынок электроники.", "indoor": True},
    {"city_name": "Шэньчжэнь", "name": "Coco Park", "desc": "Популярный ТЦ и центр ночной жизни.", "indoor": True},
    {"city_name": "Шэньчжэнь", "name": "Shenzhen Museum", "desc": "История развития города из деревни в мегаполис.", "indoor": True},
    {"city_name": "Шэньчжэнь", "name": "Sea World Shekou", "desc": "Район с кораблем Минхуа и ресторанами.", "indoor": False},
    {"city_name": "Шэньчжэнь", "name": "Dafen Oil Painting Village", "desc": "Деревня художников-копиистов.", "indoor": False},

    # Чжанцзяцзе
    {"city_name": "Чжанцзяцзе", "name": "Tianmen Mountain", "desc": "Гора с аркой 'Небесные врата'.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Yuanjiajie", "desc": "Горы Аватара и самый высокий лифт.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Yellow Dragon Cave", "desc": "Огромная карстовая пещера.", "indoor": True},
    {"city_name": "Чжанцзяцзе", "name": "Baofeng Lake", "desc": "Чистое горное озеро.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Zhangjiajie Glass Bridge", "desc": "Знаменитый стеклянный мост над каньоном.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Golden Whip Stream", "desc": "Живописная тропа вдоль ручья.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Ten-mile Gallery", "desc": "Долина с необычными скалами.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Tujia Folk Customs Park", "desc": "Парк культуры народности туцзя.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Yangjiajie", "desc": "Удаленная часть парка с 'каменной стеной'.", "indoor": False},
    {"city_name": "Чжанцзяцзе", "name": "Tianzi Mountain", "desc": "Гора с захватывающими видами на пики.", "indoor": False},

    # Сиань
    {"city_name": "Сиань", "name": "Terracotta Army", "desc": "Легендарная Терракотовая армия.", "indoor": True},
    {"city_name": "Сиань", "name": "Ancient City Wall", "desc": "Полностью сохранившаяся городская стена.", "indoor": False},
    {"city_name": "Сиань", "name": "Giant Wild Goose Pagoda", "desc": "Символ города, буддийская пагода VII века.", "indoor": False},
    {"city_name": "Сиань", "name": "Muslim Quarter", "desc": "Колоритный рынок и старинная мечеть.", "indoor": False},
    {"city_name": "Сиань", "name": "Bell Tower", "desc": "Башня в самом центре города.", "indoor": True},
    {"city_name": "Сиань", "name": "Drum Tower", "desc": "Башня с коллекцией барабанов.", "indoor": True},
    {"city_name": "Сиань", "name": "Shaanxi History Museum", "desc": "Один из лучших исторических музеев Китая.", "indoor": True},
    {"city_name": "Сиань", "name": "Stele Forest", "desc": "Музей каллиграфии на каменных стелах.", "indoor": True},
    {"city_name": "Сиань", "name": "Small Wild Goose Pagoda", "desc": "Тихая пагода в окружении парка.", "indoor": False},
    {"city_name": "Сиань", "name": "Huaqing Palace", "desc": "Дворцовый комплекс с термальными источниками.", "indoor": False},

    # Чунцин
    {"city_name": "Чунцин", "name": "Hongya Cave", "desc": "Многоуровневый комплекс в традиционном стиле на скале.", "indoor": False},
    {"city_name": "Чунцин", "name": "Ciqikou Ancient Town", "desc": "Старый город с уличной едой и сувенирами.", "indoor": False},
    {"city_name": "Чунцин", "name": "Jiefangbei Central Business District", "desc": "Центр города с небоскребами.", "indoor": False},
    {"city_name": "Чунцин", "name": "Three Gorges Museum", "desc": "Музей истории Янцзы и региона.", "indoor": True},
    {"city_name": "Чунцин", "name": "Liziba Station", "desc": "Знаменитая станция метро, проходящая сквоща дом.", "indoor": False},
    {"city_name": "Чунцин", "name": "Yangtze River Cableway", "desc": "Канатная дорога над рекой Янцзы.", "indoor": False},
    {"city_name": "Чунцин", "name": "Eling Park", "desc": "Парк на холме с панорамным видом.", "indoor": False},
    {"city_name": "Чунцин", "name": "Chongqing Zoo", "desc": "Зоопарк, известный своими пандами.", "indoor": False},
    {"city_name": "Чунцин", "name": "Raffles City Chongqing", "desc": "Футуристичный комплекс в форме парусов.", "indoor": True},
    {"city_name": "Чунцин", "name": "Dazu Rock Carvings", "desc": "Древние наскальные рельефы (за городом).", "indoor": False},

    # --- ЯПОНИЯ ---
    # Токио
    {"city_name": "Токио", "name": "Senso-ji Temple", "desc": "Старейший храм Токио в районе Асакуса.", "indoor": False},
    {"city_name": "Токио", "name": "Tokyo Skytree", "desc": "Самая высокая телебашня Японии.", "indoor": True},
    {"city_name": "Токио", "name": "Meiji Jingu Shrine", "desc": "Синтоистское святилище в лесу посреди города.", "indoor": False},
    {"city_name": "Токио", "name": "Shibuya Crossing", "desc": "Самый оживленный перекресток в мире.", "indoor": False},
    {"city_name": "Токио", "name": "Ueno Park", "desc": "Парк с музеями и зоопарком.", "indoor": False},
    {"city_name": "Токио", "name": "Akihabara Electric Town", "desc": "Район электроники, аниме и игр.", "indoor": False},
    {"city_name": "Токио", "name": "Ghibli Museum", "desc": "Музей студии анимации Миядзаки.", "indoor": True},
    {"city_name": "Токио", "name": "TeamLab Planets", "desc": "Цифровой художественный музей.", "indoor": True},
    {"city_name": "Токио", "name": "Tsukiji Outer Market", "desc": "Рынок свежих морепродуктов.", "indoor": False},
    {"city_name": "Токио", "name": "Shinjuku Gyoen", "desc": "Прекрасный сад, смешивающий три стиля.", "indoor": False},

    # --- ЮЖНАЯ КОРЕЯ ---
    # Сеул
    {"city_name": "Сеул", "name": "Gyeongbokgung Palace", "desc": "Главный королевский дворец Кореи.", "indoor": False},
    {"city_name": "Сеул", "name": "Bukchon Hanok Village", "desc": "Традиционная деревня с домами-ханоками.", "indoor": False},
    {"city_name": "Сеул", "name": "N Seoul Tower", "desc": "Символ Сеула на горе Намсан.", "indoor": True},
    {"city_name": "Сеул", "name": "Myeongdong", "desc": "Район шопинга и уличной еды.", "indoor": False},
    {"city_name": "Сеул", "name": "Dongdaemun Design Plaza", "desc": "Футуристичный центр дизайна.", "indoor": True},
    {"city_name": "Сеул", "name": "Insadong Street", "desc": "Улица антиквариата и традиционных ремесел.", "indoor": False},
    {"city_name": "Сеул", "name": "Lotte World", "desc": "Огромный парк развлечений (крытый и открытый).", "indoor": True},
    {"city_name": "Сеул", "name": "Changdeokgung Palace", "desc": "Дворец с великолепным Тайным садом.", "indoor": False},
    {"city_name": "Сеул", "name": "The War Memorial of Korea", "desc": "Масштабный военный музей.", "indoor": True},
    {"city_name": "Сеул", "name": "Cheonggyecheon Stream", "desc": "Отреставрированный ручей в центре города.", "indoor": False},

    # --- ТАИЛАНД ---
    # Бангкок
    {"city_name": "Бангкок", "name": "The Grand Palace", "desc": "Бывшая резиденция королей Сиама.", "indoor": False},
    {"city_name": "Бангкок", "name": "Wat Pho", "desc": "Храм Лежащего Будды.", "indoor": False},
    {"city_name": "Бангкок", "name": "Wat Arun", "desc": "Белоснежный Храм Рассвета.", "indoor": False},
    {"city_name": "Бангкок", "name": "Chatuchak Weekend Market", "desc": "Огромный рынок выходного дня.", "indoor": False},
    {"city_name": "Бангкок", "name": "ICONSIAM", "desc": "Ультрасовременный торговый центр на реке.", "indoor": True},
    {"city_name": "Бангкок", "name": "Jim Thompson House", "desc": "Музей традиционной тайской архитектуры.", "indoor": True},
    {"city_name": "Бангкок", "name": "Lumpini Park", "desc": "Зеленый оазис в центре Бангкока.", "indoor": False},
    {"city_name": "Бангкок", "name": "Khao San Road", "desc": "Легендарная улица бэкпекеров.", "indoor": False},
    {"city_name": "Бангкок", "name": "Sea Life Ocean World", "desc": "Большой океанариум в ТЦ Siam Paragon.", "indoor": True},
    {"city_name": "Бангкок", "name": "Wat Saket (Golden Mount)", "desc": "Храм на холме с панорамным видом.", "indoor": False},
]

async def seed_pois():
    maps_client = GoogleMapsClient()
    
    async with AsyncSessionLocal() as session:
        # Инициализируем сервис, который умеет работать с координатами
        poi_service = POIService(session)
        
        for item in RAW_POIS:
            result = await session.execute(select(City).where(City.name == item["city_name"]))
            city = result.scalars().first()
            
            if not city:
                logger.warning(f"Пропуск: Город '{item['city_name']}' не найден в БД.")
                continue
                
            query = f"{item['name']} {city.name}"
            logger.info(f"Ищем в Google: {query}")
            
            search_results = await maps_client.search_places(query)
            
            if not search_results:
                logger.error(f"  ❌ Google ничего не нашел для: {item['name']}")
                continue
                
            best_match = search_results[0]
            
            # Приоритет: берем инфо из Google, если нет - из нашего списка
            final_desc = best_match.get("description") or item["desc"]
            final_info = best_match.get("information") or "Нет дополнительной информации"

            try:
                # Используем метод сервиса, чтобы корректно создать PostGIS geom
                await poi_service.create(
                    name=item["name"],
                    description=final_desc,
                    information=final_info,
                    lat=best_match["coordinates"]["lat"],
                    lon=best_match["coordinates"]["lng"],
                    is_indoor=item["indoor"],
                    city_id=city.id
                )
                logger.info(f"  ✅ Успешно сохранено: {item['name']}")
            except Exception as e:
                logger.error(f"  ❌ Ошибка БД при сохранении {item['name']}: {e}")
                
        await session.commit()
        logger.info("🎉 Автоматическое заполнение завершено!")

if __name__ == "__main__":
    asyncio.run(seed_pois())