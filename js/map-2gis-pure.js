// Карта на базе только 2ГИС API (полностью без OpenStreetMap)
class EcoMap2GISPure {
    constructor() {
        this.map = null;
        this.markers = [];
        this.currentLocation = null;
        this.apiKey = 'demo'; // Demo ключ 2ГИС
        this.init();
    }

    async init() {
        // Инициализируем карту с базовым слоем 2ГИС
        this.map = L.map('map').setView([55.7558, 37.6173], 5); // Москва по умолчанию

        // Добавляем основной слой 2ГИС
        const dgisLayer = L.tileLayer('https://tile{s}.maps.2gis.com/tiles?x={x}&y={y}&z={z}&v=1&ngs=1', {
            attribution: '© 2ГИС',
            maxZoom: 19,
            subdomains: ['0', '1', '2', '3']
        }).addTo(this.map);

        // Добавляем дополнительные слои 2ГИС
        const satelliteLayer = L.tileLayer('https://tile{s}.maps.2gis.com/tiles?x={x}&y={y}&z={z}&v=1&ngs=1&stype=satellite', {
            attribution: '© 2ГИС (Спутник)',
            maxZoom: 19,
            subdomains: ['0', '1', '2', '3']
        });

        // Контроль слоев
        const baseMaps = {
            "2ГИС Схема": dgisLayer,
            "2ГИС Спутник": satelliteLayer
        };
        
        L.control.layers(baseMaps).addTo(this.map);
        
        console.log('Карта 2ГИС инициализирована');
        
        // Получаем геолокацию пользователя
        this.getUserLocation();
    }

    getUserLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.currentLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    
                    // Центрируем карту на местоположении пользователя
                    this.map.setView([this.currentLocation.lat, this.currentLocation.lon], 10);
                    
                    // Добавляем маркер пользователя
                    this.addUserMarker();
                },
                (error) => {
                    console.log('Геолокация недоступна:', error);
                    // Оставляем стандартный вид на Москву
                }
            );
        }
    }

    addUserMarker() {
        if (this.currentLocation) {
            const userIcon = L.divIcon({
                html: '📍',
                iconSize: [20, 20],
                className: 'user-location-marker'
            });
            
            L.marker([this.currentLocation.lat, this.currentLocation.lon], { icon: userIcon })
                .addTo(this.map)
                .bindPopup('Ваше местоположение')
                .openPopup();
        }
    }

    async searchLocation(query) {
        try {
            console.log(`Поиск локации через 2ГИС: ${query}`);
            
            const response = await fetch(
                `https://catalog.api.2gis.com/3.0/items?q=${encodeURIComponent(query)}&type=address&key=${this.apiKey}&page_size=10`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.result || !data.result.items) {
                console.log('Ничего не найдено');
                return [];
            }
            
            const locations = data.result.items.map(item => ({
                name: item.name || item.address_name || 'Без названия',
                lat: item.point?.lat,
                lon: item.point?.lon,
                type: item.type?.name || 'address',
                full_name: item.full_name || item.name || item.address_name
            })).filter(loc => loc.lat && loc.lon);
            
            // Очищаем предыдущие маркеры
            this.clearMarkers();
            
            locations.forEach(location => {
                const marker = L.marker([location.lat, location.lon])
                    .addTo(this.map)
                    .bindPopup(`
                        <strong>${location.name}</strong><br>
                        ${location.full_name || location.name}<br>
                        <small>Источник: 2ГИС</small>
                    `);
                
                this.markers.push(marker);
            });
            
            // Если есть результаты, центрируем карту на первом
            if (locations.length > 0) {
                const firstLocation = locations[0];
                this.map.setView([firstLocation.lat, firstLocation.lon], 12);
            }
            
            console.log(`Найдено ${locations.length} локаций через 2ГИС`);
            return locations;
            
        } catch (error) {
            console.error('Ошибка поиска через 2ГИС:', error);
            
            // Показываем сообщение об ошибке
            const placesContent = document.getElementById('placesContent');
            if (placesContent) {
                placesContent.innerHTML = '<div style="text-align: center; padding: 20px; color: red;">❌ Ошибка поиска. Попробуйте другой запрос.</div>';
            }
            
            return [];
        }
    }

    async findNearbyParks(lat, lon, radius = 30000) {
        try {
            const placesContent = document.getElementById('placesContent');
            if (placesContent) {
                placesContent.innerHTML = '<div style="text-align: center; padding: 20px;">🔍 Поиск парков через 2ГИС...</div>';
            }
            
            console.log(`Поиск парков через 2ГИС: lat=${lat}, lon=${lon}, radius=${radius}`);
            
            const parks = [];
            const types = [
                { query: 'парк', type: 'park', icon: '🌳' },
                { query: 'сад', type: 'garden', icon: '🌺' },
                { query: 'лес', type: 'forest', icon: '🌲' },
                { query: 'сквер', type: 'square', icon: '🏞️' },
                { query: 'заповедник', type: 'nature_reserve', icon: '🦌' },
                { query: 'бульвар', type: 'boulevard', icon: '🌿' }
            ];
            
            // Ищем по каждому типу
            for (const typeInfo of types) {
                try {
                    const response = await fetch(
                        `https://catalog.api.2gis.com/3.0/items?q=${typeInfo.query}&point=${lon},${lat}&radius=${radius}&key=${this.apiKey}&page_size=20`
                    );
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        if (data.result && data.result.items) {
                            const typeParks = data.result.items.map(item => {
                                const name = item.name || 'Без названия';
                                const point = item.point;
                                
                                if (!point) return null;
                                
                                return {
                                    name: name,
                                    lat: point.lat,
                                    lon: point.lon,
                                    type: typeInfo.type,
                                    icon: typeInfo.icon,
                                    tags: { 
                                        name: name, 
                                        type: typeInfo.type,
                                        subtype: item.subtype?.name,
                                        address: item.address_name
                                    },
                                    source: '2ГИС'
                                };
                            }).filter(park => park !== null);
                            
                            parks.push(...typeParks);
                        }
                    }
                    
                    // Небольшая задержка между запросами
                    await new Promise(resolve => setTimeout(resolve, 300));
                    
                } catch (error) {
                    console.log(`Ошибка поиска ${typeInfo.query}:`, error);
                }
            }
            
            // Удаляем дубликаты по координатам
            const uniqueParks = parks.filter((park, index, self) => 
                index === self.findIndex((p) => 
                    Math.abs(p.lat - park.lat) < 0.0001 && Math.abs(p.lon - park.lon) < 0.0001
                )
            );
            
            console.log(`Найдено ${uniqueParks.length} уникальных парков через 2ГИС`);
            
            // Очищаем предыдущие маркеры
            this.clearMarkers();
            
            // Добавляем маркеры на карту
            uniqueParks.forEach(park => {
                const customIcon = L.divIcon({
                    html: park.icon,
                    iconSize: [20, 20],
                    className: 'park-marker'
                });
                
                const popupContent = `
                    <strong>${park.name}</strong><br>
                    Тип: ${this.getTypeName(park.type)}<br>
                    ${park.tags.address ? `Адрес: ${park.tags.address}<br>` : ''}
                    <small>Источник: 2ГИС</small>
                `;
                
                const marker = L.marker([park.lat, park.lon], { icon: customIcon })
                    .addTo(this.map)
                    .bindPopup(popupContent);
                
                this.markers.push(marker);
            });
            
            // Центрируем карту на найденных парках
            if (uniqueParks.length > 0) {
                const group = new L.featureGroup(this.markers);
                this.map.fitBounds(group.getBounds().pad(0.1));
            } else {
                // Если ничего не найдено, показываем сообщение
                if (placesContent) {
                    placesContent.innerHTML = '<div style="text-align: center; padding: 20px;">🌳 Парки не найдены в указанном радиусе</div>';
                }
            }
            
            return uniqueParks;
            
        } catch (error) {
            console.error('Ошибка поиска парков:', error);
            
            const placesContent = document.getElementById('placesContent');
            if (placesContent) {
                placesContent.innerHTML = '<div style="text-align: center; padding: 20px; color: red;">❌ Ошибка поиска парков</div>';
            }
            
            return [];
        }
    }

    getTypeName(type) {
        const typeNames = {
            'park': 'Парк',
            'garden': 'Сад',
            'forest': 'Лес',
            'square': 'Сквер',
            'nature_reserve': 'Заповедник',
            'boulevard': 'Бульвар'
        };
        return typeNames[type] || type;
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }

    setView(lat, lon, zoom = 12) {
        this.map.setView([lat, lon], zoom);
    }

    // Получить текущий центр карты
    getCenter() {
        return this.map.getCenter();
    }
}

// Глобальная функция для инициализации карты только с 2ГИС
function initializeMap2GISPure() {
    if (typeof L !== 'undefined') {
        console.log('Инициализация карты 2ГИС...');
        window.ecoMap = new EcoMap2GISPure();
        return true;
    } else {
        console.error('Leaflet не загружен');
        return false;
    }
}

console.log('Pure 2GIS Map module loaded');
