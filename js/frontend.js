const API_URL = 'http://127.0.0.1:8000/api';
let currentFilters = { type: 'all', region: 'all', search: '' };
let currentView = 'calendar';
let allHolidays = [];
let currentHolidayId = null;
let currentUser = null;
let calendarMonth = new Date().getMonth();
let calendarYear = new Date().getFullYear();
let userLocation = null;

// Конфигурация ролей — легко добавлять/удалять/изменять
const USER_ROLES = {
    0: { label: 'Пользователь', class: 'user', icon: '👤' },
    1: { label: 'Администратор', class: 'admin', icon: '👑' },
};

// Вспомогательная функция для получения данных роли
function getRoleInfo(role) {
    return USER_ROLES[role] || { label: 'Неизвестно', class: 'unknown', icon: '❓' };
}

// Проверка при загрузке
if (localStorage.getItem('user')) {
    currentUser = JSON.parse(localStorage.getItem('user'));
    updateUserUI();
}

// Календарь

const typeLabels = { eco: 'Экология', national: 'Национальный', world: 'Мировой' };
const typeClasses = { eco: 'type-eco', national: 'type-national', world: 'type-world' };
const regionLabels = { russia: 'Россия', world: 'Весь мир' };
const months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
    'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'];
const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];

// Инициализация селекта месяцев (вызывается при загрузке)
function initMonthSelect() {
    const monthSelect = document.getElementById('monthSelect');
    if (monthSelect && monthSelect.options.length === 0) {
        monthNames.forEach((name, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = name;
            monthSelect.appendChild(option);
        });
        monthSelect.value = calendarMonth;
    }
    const yearInput = document.getElementById('yearInput');
    if (yearInput) {
        yearInput.value = calendarYear;
    }
}

// Переключение вида
function switchView(view) {
    currentView = view;

    // Обновляем кнопки
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    // Показываем/скрываем контейнеры
    document.getElementById('gridView').style.display = view === 'grid' ? 'block' : 'none';
    document.getElementById('calendarView').style.display = view === 'calendar' ? 'block' : 'none';
    document.getElementById('mapView').style.display = view === 'map' ? 'block' : 'none';

    if (view === 'calendar') {
        renderCalendar();
    } else if (view === 'grid') {
        renderGrid();
    } else if (view === 'map') {
        // Инициализируем карту при переключении на вид карты
        setTimeout(() => {
            if (!window.ecoMap) {
                initializeMap2GISPure();
            } else {
                // Обновляем размер карты
                window.ecoMap.map.invalidateSize();
            }
        }, 100);
    }
}

function updateUserUI() {
    if (currentUser) {
        document.getElementById('userArea').style.display = 'none';
        document.getElementById('adminArea').style.display = 'flex';
        document.getElementById('userName').textContent = currentUser.name;

        // Отображение роли
        const roleInfo = getRoleInfo(currentUser.role);
        const userNameEl = document.getElementById('userName');
        userNameEl.textContent = `${roleInfo.icon} ${currentUser.name} (${roleInfo.label})`;

        // Показываем кнопки админа только для админов
        const adminBtns = document.querySelectorAll('.admin-only');
        adminBtns.forEach(b => b.style.display = currentUser.role === 1 ? 'inline-block' : 'none');

        // Кнопка "+ Праздник" видна только админу
        document.querySelector('.btn-admin').style.display = currentUser.role === 1 ? 'inline-block' : 'none';
    } else {
        document.getElementById('userArea').style.display = 'flex';
        document.getElementById('adminArea').style.display = 'none';
    }
}

function showLogin() {
    const formHtml = `
        <div class="auth-form">
            <h2>🔑 Вход в систему</h2>
            <div class="form-group">
                <label for="loginEmail">Email</label>
                <input type="email" id="loginEmail" placeholder="Введите ваш email">
            </div>
            <div class="form-group">
                <label for="loginPassword">Пароль</label>
                <input type="password" id="loginPassword" placeholder="Введите ваш пароль">
            </div>
            <button onclick="login()">Войти</button>
            <p class="form-switch" onclick="showRegister()">Нет аккаунта? Зарегистрироваться</p>
        </div>
    `;

    document.getElementById('authModalBody').innerHTML = formHtml;
    document.getElementById('authModal').classList.add('active');
}

function showRegister() {
    const formHtml = `
        <div class="auth-form">
            <h2>📝 Регистрация</h2>
            <div class="form-group">
                <label for="regLastName">Фамилия</label>
                <input type="text" id="regLastName" placeholder="Введите вашу фамилию">
            </div>
            <div class="form-group">
                <label for="regFirstName">Имя</label>
                <input type="text" id="regFirstName" placeholder="Введите ваше имя">
            </div>
            <div class="form-group">
                <label for="regPatronymic">Отчество (необязательно)</label>
                <input type="text" id="regPatronymic" placeholder="Введите отчество">
            </div>
            <div class="form-group">
                <label for="regEmail">Email</label>
                <input type="email" id="regEmail" placeholder="Введите ваш email">
            </div>
            <div class="form-group">
                <label for="regPassword">Пароль</label>
                <input type="password" id="regPassword" placeholder="Придумайте пароль">
            </div>
            <button onclick="register()">Зарегистрироваться</button>
            <p class="form-switch" onclick="showLogin()">Уже есть аккаунт? Войти</p>
        </div>
    `;

    document.getElementById('authModalBody').innerHTML = formHtml;
    document.getElementById('authModal').classList.add('active');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
}

async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            currentUser = await response.json();
            localStorage.setItem('user', JSON.stringify(currentUser));
            updateUserUI();
            closeAuthModal();
        } else {
            const error = await response.json();
            alert('Ошибка: ' + error.detail);
        }
    } catch (error) {
        alert('Ошибка соединения с сервером');
    }
}

async function importHolidays() {
    if (!currentUser || currentUser.role !== 1) {
        alert('Только администратор может импортировать праздники');
        return;
    }

    if (!confirm('Импортировать праздники из внешнего API? Это добавит новые международные праздники.')) return;

    try {
        const response = await fetch(`${API_URL}/import/holidays`);
        const data = await response.json();
        alert(`✅ ${data.message}`);
        loadHolidays(); // Перезагружаем список
    } catch (error) {
        alert('Ошибка импорта');
    }
}

async function register() {
    const data = {
        last_name: document.getElementById('regLastName').value,
        first_name: document.getElementById('regFirstName').value,
        patronymic: document.getElementById('regPatronymic').value || null,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value
    };

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Регистрация успешна! Теперь войдите.');
            showLogin();
        } else {
            const error = await response.json();
            alert('Ошибка: ' + error.detail);
        }
    } catch (error) {
        alert('Ошибка соединения с сервером');
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('user');
    updateUserUI();
}

function showAddHolidayForm() {
    if (!currentUser || currentUser.role !== 1) {
        alert('Только администратор может добавлять праздники');
        return;
    }

    // Удаляем старую форму если есть
    const oldForm = document.getElementById('add-holiday-form-modal');
    if (oldForm) oldForm.remove();

    const modal = document.createElement('div');
    modal.id = 'add-holiday-form-modal';
    modal.className = 'modal active';
    modal.style.zIndex = '2001';
    modal.onclick = function (e) { if (e.target === this) this.remove(); };

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <button class="close-btn" onclick="document.getElementById('add-holiday-form-modal').remove()" style="color: white;">✕</button>
                <h2 style="color: white; font-size: 22px;">➕ Новый праздник</h2>
            </div>
            <div class="modal-body">
                <div class="auth-form" style="box-shadow: none; padding: 0;">
                    <div class="form-group">
                        <label for="newName">Название</label>
                        <input type="text" id="newName" placeholder="Введите название праздника">
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div class="form-group" style="flex: 1;">
                            <label for="newDay">День</label>
                            <input type="number" id="newDay" placeholder="1-31" min="1" max="31">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label for="newMonth">Месяц</label>
                            <select id="newMonth" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                                ${monthNames.map((m, i) => `<option value="${i}">${m}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="newType">Тип</label>
                        <select id="newType" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                            <option value="eco">🌿 Экологический</option>
                            <option value="national">🇷🇺 Национальный</option>
                            <option value="world">🌍 Мировой</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="newRegion">Регион</label>
                        <select id="newRegion" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                            <option value="russia">🇷🇺 Россия</option>
                            <option value="world">🌍 Весь мир</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="newDescription">Описание</label>
                        <textarea id="newDescription" placeholder="Введите описание праздника" rows="4" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="newEvents">Мероприятия (через запятую)</label>
                        <input type="text" id="newEvents" placeholder="Например: Парад, Концерт, Фейерверк">
                    </div>
                    <div class="form-group">
                        <label for="newWikiUrl">Ссылка на Википедию</label>
                        <input type="url" id="newWikiUrl" placeholder="https://ru.wikipedia.org/...">
                    </div>
                    <button onclick="addHoliday()" style="margin-top: 10px;">💾 Сохранить праздник</button>
                    <p class="form-switch" onclick="document.getElementById('add-holiday-form-modal').remove()">Отмена</p>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

async function addHoliday() {
    const events = document.getElementById('newEvents').value
        .split(',')
        .map(e => e.trim())
        .filter(e => e);

    const data = {
        name: document.getElementById('newName').value,
        day: parseInt(document.getElementById('newDay').value),
        month: parseInt(document.getElementById('newMonth').value),
        type: document.getElementById('newType').value,
        region: document.getElementById('newRegion').value,
        description: document.getElementById('newDescription').value,
        events: events,
        wikipedia_url: document.getElementById('newWikiUrl').value
    };

    // Проверка на дубликат
    const isDuplicate = await checkHolidayDuplicate(data.name, data.day, data.month);
    if (isDuplicate) {
        alert('⚠️ Праздник с таким названием уже существует!');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/holidays`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            document.getElementById('add-holiday-form-modal').remove();
            loadHolidays();
            alert('✅ Праздник добавлен');
        }
    } catch (error) {
        alert('Ошибка при добавлении');
    }
}

// Загрузка данных
async function loadHolidays() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.type !== 'all') params.append('type', currentFilters.type);
        if (currentFilters.region !== 'all') params.append('region', currentFilters.region);
        if (currentFilters.search) params.append('search', currentFilters.search);

        const response = await fetch(`${API_URL}/holidays?${params}`);
        allHolidays = await response.json();

        if (currentView === 'grid') {
            renderGrid();
        } else {
            renderCalendar();
        }
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        const container = document.getElementById('holidaysContainer');
        container.innerHTML = '<div class="loading" style="color: red;">❌ Ошибка загрузки. Проверьте, запущен ли сервер на http://127.0.0.1:8000</div>';
    }
}

// Сетка (карточки)
function renderGrid() {
    const container = document.getElementById('holidaysContainer');

    if (!allHolidays || allHolidays.length === 0) {
        container.innerHTML = `
                    <div class="empty" style="grid-column: 1/-1;">
                        <div class="empty-icon">🌍</div>
                        <h3>Ничего не найдено</h3>
                        <p>Попробуйте изменить параметры поиска</p>
                    </div>`;
        return;
    }

    container.innerHTML = allHolidays.map(holiday => `
                <div class="holiday-card" onclick="openModal(${holiday.id})">
                    <div class="card-header">
                        <div class="date-badge">📅 ${holiday.day} ${months[holiday.month]}</div>
                        <div class="type-badge ${typeClasses[holiday.type]}">${typeLabels[holiday.type]}</div>
                    </div>
                    <h2>${holiday.name}</h2>
                    <p>${holiday.description.substring(0, 150)}...</p>
                    <div class="card-footer">
                        <span>📍 ${regionLabels[holiday.region]}</span>
                        <span>🏷️ ${typeLabels[holiday.type]}</span>
                    </div>
                </div>
            `).join('');
}

// Календарь
async function renderCalendar() {
    document.getElementById('calendarMonthTitle').textContent =
        `${monthNames[calendarMonth]} ${calendarYear}`;

    // Обновляем селект месяца и поле года
    const monthSelect = document.getElementById('monthSelect');
    if (monthSelect) {
        if (monthSelect.options.length === 0) {
            monthNames.forEach((name, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = name;
                monthSelect.appendChild(option);
            });
        }
        monthSelect.value = calendarMonth;
    }
    const yearInput = document.getElementById('yearInput');
    if (yearInput) {
        yearInput.value = calendarYear;
    }

    const daysContainer = document.getElementById('calendarDays');

    // Получаем выходные дни для этого месяца
    try {
        const response = await fetch(`${API_URL}/work-days?year=${calendarYear}&month=${calendarMonth}`);
        const workDays = await response.json();

        // Первый день месяца
        const firstDay = new Date(calendarYear, calendarMonth, 1);
        // Последний день месяца
        const lastDay = new Date(calendarYear, calendarMonth + 1, 0);

        // День недели первого дня (Пн=0, Вс=6)
        let startDay = firstDay.getDay() - 1;
        if (startDay < 0) startDay = 6;

        let html = '';

        // Пустые ячейки перед первым днем
        for (let i = 0; i < startDay; i++) {
            html += '<div class="day-cell other-month"></div>';
        }

        // Дни месяца
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dayHolidays = allHolidays.filter(h =>
                h.day === day && h.month === calendarMonth
            );

            const workDay = workDays.find(w => w.day === day);
            const isWeekend = workDay ? workDay.is_weekend : 0;
            const isHoliday = workDay ? workDay.is_holiday : 0;

            const isToday = (day === new Date().getDate() &&
                calendarMonth === new Date().getMonth() &&
                calendarYear === new Date().getFullYear());

            let cellClass = 'day-cell';
            if (isToday) cellClass += ' today';
            if (isWeekend === 1) cellClass += ' weekend';
            if (isWeekend === 2 || isHoliday === 1) cellClass += ' holiday';

            html += `<div class="${cellClass}">`;
            html += `<div class="day-number">${day}</div>`;

            // Не показываем статус дня, только праздники

            // Показываем первые 2 праздника
            const maxShow = 2;
            dayHolidays.slice(0, maxShow).forEach(h => {
                html += `<div class="day-holiday ${h.type}" onclick="event.stopPropagation(); openModal(${h.id})" title="${h.name}">${h.name.substring(0, 25)}</div>`;
            });

            if (dayHolidays.length > maxShow) {
                html += `<div class="more-badge" onclick="event.stopPropagation(); showDayHolidays(${day}, ${calendarMonth}, ${calendarYear})">+${dayHolidays.length - maxShow} ещё</div>`;
            }

            html += '</div>';
        }

        daysContainer.innerHTML = html;
    } catch (error) {
        console.error('Ошибка загрузки выходных дней:', error);
        // Fallback - показываем только праздники
        renderCalendarFallback();
    }
}

function showDayHolidays(day, month, year) {
    const dayHolidays = allHolidays.filter(h =>
        h.day === day && h.month === month
    );

    if (dayHolidays.length === 0) return;

    const dateStr = `${day} ${monthNames[month]} ${year}`;

    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.style.zIndex = '2000';
    modal.onclick = function (e) { if (e.target === this) this.remove(); };

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header" style="padding: 30px;">
                <button class="close-btn" onclick="this.closest('.modal').remove()" style="color: white;">✕</button>
                <h2 style="color: white; font-size: 22px;">📅 ${dateStr}</h2>
                <p style="color: rgba(255,255,255,0.8); margin-top: 10px;">Праздники этого дня</p>
            </div>
            <div class="modal-body" style="padding: 30px;">
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    ${dayHolidays.map(h => `
                        <div onclick="document.querySelector('.modal.active[style*=\\'z-index: 2000\\']').remove(); openModal(${h.id})" 
                             style="padding: 15px; background: #f5f5f0; border-radius: 12px; cursor: pointer; transition: all 0.2s; border-left: 4px solid ${h.type === 'eco' ? '#4caf50' : h.type === 'national' ? '#2196F3' : '#9C27B0'};"
                             onmouseover="this.style.transform='translateX(5px)'; this.style.background='#e8f5e9';" 
                             onmouseout="this.style.transform=''; this.style.background='#f5f5f0';">
                            <div style="font-weight: 600; color: #5A5A40; margin-bottom: 5px;">${h.name}</div>
                            <div style="font-size: 13px; color: #666;">${h.description.substring(0, 100)}...</div>
                            <div style="margin-top: 8px;">
                                <span class="type-badge ${typeClasses[h.type]}" style="font-size: 11px;">${typeLabels[h.type]}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

function goToSelectedMonth() {
    const monthSelect = document.getElementById('monthSelect');
    const yearInput = document.getElementById('yearInput');

    if (monthSelect) {
        calendarMonth = parseInt(monthSelect.value);
    }
    if (yearInput) {
        const year = parseInt(yearInput.value);
        if (year >= 2000 && year <= 2100) {
            calendarYear = year;
        }
    }
    loadHolidays();
}

// Fallback функция для календаря без выходных дней
function renderCalendarFallback() {
    const daysContainer = document.getElementById('calendarDays');

    // Первый день месяца
    const firstDay = new Date(calendarYear, calendarMonth, 1);
    // Последний день месяца
    const lastDay = new Date(calendarYear, calendarMonth + 1, 0);

    // День недели первого дня (Пн=0, Вс=6)
    let startDay = firstDay.getDay() - 1;
    if (startDay < 0) startDay = 6;

    let html = '';

    // Пустые ячейки перед первым днем
    for (let i = 0; i < startDay; i++) {
        html += '<div class="day-cell other-month"></div>';
    }

    // Дни месяца
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayHolidays = allHolidays.filter(h =>
            h.day === day && h.month === calendarMonth
        );

        const isToday = (day === new Date().getDate() &&
            calendarMonth === new Date().getMonth() &&
            calendarYear === new Date().getFullYear());

        // Определяем выходные по дням недели (суббота, воскресенье)
        const dayOfWeek = new Date(calendarYear, calendarMonth, day).getDay();
        const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);

        let cellClass = 'day-cell';
        if (isToday) cellClass += ' today';
        if (isWeekend) cellClass += ' weekend';

        html += `<div class="${cellClass}">`;
        html += `<div class="day-number">${day}</div>`;

        // Не показываем статус дня, только праздники

        // Показываем первые 2 праздника
        const maxShow = 2;
        dayHolidays.slice(0, maxShow).forEach(h => {
            html += `<div class="day-holiday ${h.type}" onclick="event.stopPropagation(); openModal(${h.id})" title="${h.name}">${h.name.substring(0, 25)}</div>`;
        });

        if (dayHolidays.length > maxShow) {
            html += `<div class="more-badge">+${dayHolidays.length - maxShow} ещё</div>`;
        }

        html += '</div>';
    }

    daysContainer.innerHTML = html;
}

function prevMonth() {
    if (calendarMonth === 0) {
        calendarMonth = 11;
        calendarYear--;
    } else {
        calendarMonth--;
    }
    loadHolidays();
}

function nextMonth() {
    if (calendarMonth === 11) {
        calendarMonth = 0;
        calendarYear++;
    } else {
        calendarMonth++;
    }
    loadHolidays();
}

// Модальное окно
function openModal(holidayId) {
    const holiday = allHolidays.find(h => h.id === holidayId);
    if (!holiday) return;

    document.getElementById('modalTitle').textContent = holiday.name;
    document.getElementById('modalDescription').textContent = holiday.description;

    // Бейджи
    const badgesHtml = `
                <span class="type-badge type-${holiday.type}">${typeLabels[holiday.type]}</span>
                <span class="date-badge">${holiday.day} ${monthNames[holiday.month]}</span>
            `;
    document.getElementById('modalBadges').innerHTML = badgesHtml;

    // Мероприятия
    const eventsList = document.getElementById('modalEvents');
    if (holiday.events && holiday.events.length > 0) {
        eventsList.innerHTML = holiday.events.map(event => `<li>${event}</li>`).join('');
    } else {
        eventsList.innerHTML = '<li>Мероприятия не запланированы</li>';
    }

    // Wikipedia ссылка
    const wikiLink = document.getElementById('modalWiki');
    if (holiday.wikipedia_url) {
        wikiLink.href = holiday.wikipedia_url;
        wikiLink.style.display = 'inline-block';
    } else {
        wikiLink.style.display = 'none';
    }

    // Загружаем внешние данные
    loadExternalData(holidayId);

    document.getElementById('holidayModal').classList.add('active');
    currentHolidayId = holidayId;
}

// Загрузка внешних данных для праздника
async function loadExternalData(holidayId) {
    // Показываем индикатор загрузки
    showLoadingIndicator();

    try {
        // Получаем информацию о празднике
        const holiday = allHolidays.find(h => h.id === holidayId);
        if (!holiday) return;

        // Всегда используем текущий год для праздника
        const today = new Date();
        const holidayYear = today.getFullYear();

        // Формируем дату праздника в текущем году
        const holidayDate = new Date(holidayYear, holiday.month, holiday.day);

        console.log('Дата праздника:', holidayDate.toLocaleDateString('ru-RU'));
        console.log('Дней до/после:', Math.ceil((holidayDate - today) / (1000 * 60 * 60 * 24)));

        // Загружаем только погоду за дату праздника
        await loadHolidayWeather(holidayDate);

    } catch (error) {
        console.error('Ошибка загрузки внешних данных:', error);
    } finally {
        hideLoadingIndicator();
    }
}

// Получение геолокации при загрузке сайта
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                console.log('Геолокация получена:', userLocation);
            },
            (error) => {
                console.log('Геолокация недоступна:', error);
                // Используем координаты Москвы по умолчанию
                userLocation = {
                    latitude: 55.75,
                    longitude: 37.61
                };
            }
        );
    } else {
        // Используем координаты Москвы по умолчанию
        userLocation = {
            latitude: 55.75,
            longitude: 37.61
        };
    }
}

// Загрузка погоды за дату праздника
async function loadHolidayWeather(holidayDate) {
    if (!userLocation) {
        console.log('Геолокация еще не получена');
        return;
    }

    try {
        const { latitude, longitude } = userLocation;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        holidayDate.setHours(0, 0, 0, 0);

        const daysUntilHoliday = Math.ceil((holidayDate - today) / (1000 * 60 * 60 * 24));
        console.log('Дней до праздника:', daysUntilHoliday);
        console.log('Дата праздника:', holidayDate.toLocaleDateString('ru-RU'));

        // Форматируем дату для API
        const dateString = holidayDate.toISOString().split('T')[0]; // YYYY-MM-DD

        let weatherData;
        let weatherType;

        // Запрашиваем погоду для конкретной даты
        const response = await fetch(`${API_URL}/external/weather?lat=${latitude}&lon=${longitude}&date=${dateString}`);

        if (response.ok) {
            weatherData = await response.json();

            // Определяем тип данных на основе ответа
            if (weatherData.type === 'historical_climate') {
                weatherType = 'passed';
                console.log('Используем исторические климатические данные');
            } else if (weatherData.type === 'future_climate') {
                weatherType = 'future';
                console.log('Используем будущие климатические данные');
            } else {
                weatherType = 'forecast';
                console.log('Используем прогноз погоды');
            }
        } else {
            // Fallback на старую логику
            if (daysUntilHoliday >= 0 && daysUntilHoliday <= 7) {
                const response = await fetch(`${API_URL}/external/weather?lat=${latitude}&lon=${longitude}&days=7`);
                weatherData = await response.json();
                weatherType = 'forecast';
                console.log('Используем прогноз погоды (fallback)');
            } else {
                // Климатические данные как запасной вариант
                const month = holidayDate.getMonth();
                const climateData = {
                    0: { temp: -5, desc: "Снег", humidity: 85, wind: 12, code: 71 },
                    1: { temp: -3, desc: "Снег с дождем", humidity: 80, wind: 11, code: 73 },
                    2: { temp: 2, desc: "Снег с дождем", humidity: 75, wind: 10, code: 61 },
                    3: { temp: 8, desc: "Переменная облачность", humidity: 65, wind: 8, code: 2 },
                    4: { temp: 15, desc: "Ясно", humidity: 60, wind: 7, code: 0 },
                    5: { temp: 20, desc: "Ясно", humidity: 55, wind: 6, code: 0 },
                    6: { temp: 22, desc: "Преимущественно ясно", humidity: 50, wind: 6, code: 1 },
                    7: { temp: 21, desc: "Преимущественно ясно", humidity: 55, wind: 6, code: 1 },
                    8: { temp: 15, desc: "Переменная облачность", humidity: 65, wind: 7, code: 2 },
                    9: { temp: 8, desc: "Пасмурно", humidity: 70, wind: 8, code: 3 },
                    10: { temp: 2, desc: "Переменная облачность", humidity: 75, wind: 9, code: 2 },
                    11: { temp: -3, desc: "Снег", humidity: 80, wind: 11, code: 71 }
                };

                const monthData = climateData[month] || { temp: 15, desc: "Переменная облачность", humidity: 65, wind: 10, code: 2 };

                weatherData = {
                    current: {
                        temperature_2m: monthData.temp,
                        relativehumidity_2m: monthData.humidity,
                        windspeed_10m: monthData.wind,
                        weathercode: monthData.code
                    },
                    forecast: {},
                    source: 'OpenMeteo (климатические данные)',
                    type: daysUntilHoliday < 0 ? 'passed' : 'future'
                };

                weatherType = daysUntilHoliday < 0 ? 'passed' : 'future';
                console.log('Используем климатические данные (fallback)');
            }
        }

        if (weatherData) {
            addWeatherToModal(weatherData, holidayDate, daysUntilHoliday, weatherType);
        }
    } catch (error) {
        console.error('Ошибка загрузки погоды:', error);
    }
}

// Добавление погоды в модальное окно
function addWeatherToModal(weatherData, holidayDate, daysUntilHoliday, weatherType) {
    const current = weatherData.current || weatherData; // OpenMeteo возвращает данные напрямую
    const forecast = weatherData.forecast || {};

    // Определяем тип погоды для заголовка
    let weatherTitle = 'Погода';
    if (weatherType === 'passed') {
        weatherTitle = 'Погода';
    } else if (weatherType === 'future') {
        weatherTitle = 'Ожидаемая погода';
    } else if (daysUntilHoliday === 0) {
        weatherTitle = 'Погода сегодня';
    } else if (daysUntilHoliday > 0 && daysUntilHoliday <= 7) {
        weatherTitle = 'Прогноз погоды';
    }

    // Ищем погоду на конкретную дату праздника
    let targetTemp = current.temperature_2m || 0;
    let targetWeatherCode = current.weathercode || 0;
    let weatherDescription = 'Переменная облачность';

    // Для климатических данных (прошедших и будущих) используем средние значения для месяца
    if (weatherType === 'passed' || weatherType === 'future') {
        const holidayMonth = new Date(holidayDate).getMonth();
        const climateData = {
            0: { temp: -5, desc: "Снег", humidity: 85, wind: 12 },      // Январь
            1: { temp: -3, desc: "Снег", humidity: 82, wind: 11 },      // Февраль
            2: { temp: 2, desc: "Снег с дождем", humidity: 78, wind: 10 }, // Март
            3: { temp: 10, desc: "Переменная облачность", humidity: 68, wind: 9 }, // Апрель
            4: { temp: 17, desc: "Ясно", humidity: 60, wind: 8 },       // Май
            5: { temp: 22, desc: "Ясно", humidity: 55, wind: 7 },       // Июнь
            6: { temp: 24, desc: "Ясно", humidity: 58, wind: 6 },       // Июль
            7: { temp: 23, desc: "Переменная облачность", humidity: 62, wind: 7 }, // Август
            8: { temp: 17, desc: "Переменная облачность", humidity: 70, wind: 9 }, // Сентябрь
            9: { temp: 10, desc: "Дождь", humidity: 78, wind: 11 },      // Октябрь
            10: { temp: 3, desc: "Дождь с мокрым снегом", humidity: 83, wind: 12 }, // Ноябрь
            11: { temp: -2, desc: "Снег", humidity: 86, wind: 13 }       // Декабрь
        };

        const monthData = climateData[holidayMonth] || { temp: 15, desc: "Переменная облачность", humidity: 65, wind: 10 };
        targetTemp = monthData.temp;
        weatherDescription = monthData.desc;

        // Обновляем данные для отображения
        current.relativehumidity_2m = monthData.humidity;
        current.windspeed_10m = monthData.wind;
    } else if (forecast.time && forecast.temperature_2m_max) {
        // Для ближайших 7 дней используем реальные данные прогноза
        const holidayDateObj = new Date(holidayDate);
        const holidayDateString = holidayDateObj.toISOString().split('T')[0];

        // Ищем индекс даты в прогнозе
        const dateIndex = forecast.time.findIndex(date => date === holidayDateString);
        if (dateIndex !== -1) {
            targetTemp = forecast.temperature_2m_max[dateIndex] || forecast.temperature_2m_min[dateIndex] || 0;
            targetWeatherCode = forecast.weathercode[dateIndex] || 0;
        }

        // Конвертируем weather code в описание
        const weatherDescriptions = {
            0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
            45: "Туман", 48: "Туман с инеем", 51: "Легкая морось", 53: "Умеренная морось",
            55: "Плотная морось", 56: "Легкая ледяная морось", 57: "Умеренная ледяная морось",
            61: "Слабый дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
            71: "Слабый снег", 73: "Умеренный снег", 75: "Сильный снег",
            80: "Слабые ливни", 81: "Умеренные ливни", 82: "Сильные ливни",
            95: "Гроза", 96: "Гроза с градом"
        };

        weatherDescription = weatherDescriptions[targetWeatherCode] || 'Переменная облачность';
    }

    const humidity = current.relativehumidity_2m;
    const windSpeed = current.windspeed_10m;

    // Добавляем информацию о типе данных
    let dataSource = weatherData.source || 'OpenMeteo';
    if ((weatherType === 'passed' || weatherType === 'future') && !dataSource.includes('климатические')) {
        dataSource += ' (климатические данные)';
    }

    // Получаем название местоположения
    const locationName = weatherData.location_name || '';

    const currentYear = new Date().getFullYear();
    const weatherHtml = `
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;" class="weather-section">
                    <h3 style="color: #5A5A40; margin-bottom: 15px;">🌤️ ${weatherTitle} на ${new Date(holidayDate).toLocaleDateString('ru-RU')} (${currentYear} год)</h3>
                    ${locationName ? `<p style="color: #5A5A40; font-weight: 600; margin-bottom: 15px;">📍 ${locationName}</p>` : ''}
                    <div style="display: flex; align-items: center; gap: 15px; padding: 10px; background: #f5f5f0; border-radius: 8px;">
                        <div>
                            <div style="font-size: 24px; font-weight: bold;">${Math.round(targetTemp)}°C</div>
                            <div style="font-size: 12px; color: #666;">${weatherDescription}</div>
                        </div>
                        <div>
                            <div style="font-size: 12px; color: #666;">Влажность: ${humidity || 'Н/Д'}%</div>
                            <div style="font-size: 12px; color: #666;">Ветер: ${windSpeed || 'Н/Д'} км/ч</div>
                            <div style="font-size: 12px; color: #666;">Источник: ${dataSource}</div>
                        </div>
                    </div>
                </div>
            `;

    // Добавляем погоду в конец модального окна
    const modalBody = document.querySelector('.modal-body');
    modalBody.insertAdjacentHTML('beforeend', weatherHtml);
}

// Индикатор загрузки
function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'loading-indicator';
    indicator.innerHTML = '<div style="text-align: center; padding: 20px;">⏳ Загрузка данных...</div>';
    document.querySelector('.modal-body').appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Админ панель
function showAdminPanel() {
    const adminPanel = document.createElement('div');
    adminPanel.id = 'admin-panel';
    adminPanel.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 100vh;
        background: rgba(0,0,0,0.5);
        z-index: 10000;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 50px;
        animation: fadeIn 0.3s ease;
        overflow-y: auto;
    `;

    adminPanel.innerHTML = `
        <div class="admin-panel">
            <div class="admin-section">
                <h2>⚙️ Панель администратора</h2>
                <button class="btn-admin danger" onclick="closeAdminPanel()" style="float: right; margin-bottom: 15px;">✖ Закрыть</button>
            </div>
            
            <div class="admin-stats">
                <div class="stat-card">
                    <div class="number" id="totalHolidays">0</div>
                    <div class="label">📅 Всего праздников</div>
                </div>
                <div class="stat-card">
                    <div class="number" id="totalUsers">0</div>
                    <div class="label">👥 Пользователей</div>
                </div>
                <div class="stat-card">
                    <div class="number" id="ecoHolidays">0</div>
                    <div class="label">🌿 Эко-праздников</div>
                </div>
                <div class="stat-card">
                    <div class="number" id="nationalHolidays">0</div>
                    <div class="label">🇷🇺 Нац. праздников</div>
                </div>
            </div>
            
            <div class="admin-section">
                <h3>🛠️ Управление</h3>
                <div class="admin-actions">
                    <button class="admin-action-btn" onclick="showAddHolidayForm(); closeAdminPanel();">
                        <span class="icon">➕</span>
                        <span>Добавить праздник</span>
                    </button>
                    <button class="admin-action-btn secondary" onclick="importHolidays(); closeAdminPanel();">
                        <span class="icon">📥</span>
                        <span>Импорт праздников</span>
                    </button>
                    <button class="admin-action-btn info" onclick="exportHolidays()">
                        <span class="icon">📤</span>
                        <span>Экспорт данных</span>
                    </button>
                    <button class="admin-action-btn admin-only" onclick="testAllAPIs()">
                        <span class="icon">🔧</span>
                        <span>Тест API</span>
                    </button>
                    <button class="admin-action-btn danger" onclick="clearCache()">
                        <span class="icon">🗑️</span>
                        <span>Очистить кэш</span>
                    </button>
                    <button class="admin-action-btn" onclick="showUserManagement()">
                        <span class="icon">👥</span>
                        <span>Управление пользователями</span>
                    </button>
                </div>
            </div>
            
            <div class="admin-section">
                <h3 style="color: #5A5A40; margin-top: 0;">📊 Статистика системы</h3>
                <div id="systemStats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div>🌤️ Погода: <span id="weatherStatus" style="color: #4caf50;">✅ Работает</span></div>
                    <div>📰 Новости: <span id="newsStatus" style="color: #4caf50;">✅ Работает</span></div>
                    <div>🗺️ Геолокация: <span id="geoStatus" style="color: #4caf50;">✅ Работает</span></div>
                </div>
            </div>
            
            <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #4caf50;">
                <h3 style="color: #5A5A40; margin-top: 0;">🔐 Информация о системе</h3>
                <div style="margin-top: 10px; font-family: monospace; font-size: 14px;">
                    <div>Версия: 1.0.0</div>
                    <div>Пользователь: <span id="currentUserEmail">${currentUser?.email || 'Не авторизован'}</span></div>
                    <div>Роль: <span id="currentUserRole">${getRoleInfo(currentUser?.role).label}</span></div>
                    <div>База данных: SQLite</div>
                    <div>API сервер: http://127.0.0.1:8000</div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(adminPanel);
    loadAdminStats();
}

function closeAdminPanel() {
    const panel = document.getElementById('admin-panel');
    if (panel) {
        panel.remove();
    }
}

function loadAdminStats() {
    // Загрузка статистики праздников
    fetch(`${API_URL}/holidays`)
        .then(response => response.json())
        .then(holidays => {
            const total = holidays.length;
            const eco = holidays.filter(h => h.type === 'eco').length;
            const national = holidays.filter(h => h.type === 'national').length;

            document.getElementById('totalHolidays').textContent = total;
            document.getElementById('ecoHolidays').textContent = eco;
            document.getElementById('nationalHolidays').textContent = national;
        })
        .catch(error => {
            console.error('Ошибка загрузки статистики:', error);
        });

    // Загрузка статистики пользователей (если есть эндпоинт)
    // Временно установим значение по умолчанию
    document.getElementById('totalUsers').textContent = '2';
}

function exportHolidays() {
    fetch(`${API_URL}/holidays`)
        .then(response => response.json())
        .then(holidays => {
            const dataStr = JSON.stringify(holidays, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

            const exportFileDefaultName = `holidays_${new Date().toISOString().split('T')[0]}.json`;

            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();

            alert('📤 Данные экспортированы успешно!');
        })
        .catch(error => {
            console.error('Ошибка экспорта:', error);
            alert('❌ Ошибка при экспорте данных');
        });
}

function clearCache() {
    if (confirm('⚠️ Вы уверены, что хотите очистить кэш? Это удалит все сохраненные данные.')) {
        localStorage.clear();
        sessionStorage.clear();
        location.reload();
    }
}

async function showUserManagement() {
    const userManagementPanel = document.createElement('div');
    userManagementPanel.id = 'user-management-panel';
    userManagementPanel.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 100vh;
        background: rgba(0,0,0,0.5);
        z-index: 10000;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding-top: 50px;
        animation: fadeIn 0.3s ease;
    `;

    userManagementPanel.innerHTML = `
        <div class="admin-panel">
            <div class="admin-section">
                <h2>👥 Управление пользователями</h2>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <button class="btn-admin success" onclick="showAddUserForm()">➕ Добавить пользователя</button>
                    <button class="btn-admin info" onclick="exportUsers()">📤 Экспорт пользователей</button>
                    <button class="btn-admin secondary" onclick="importUsers()">📥 Импорт пользователей</button>
                    <button class="btn-admin danger" onclick="closeUserManagement()" style="float: right;">✖ Закрыть</button>
                </div>
            </div>
            
            <div class="admin-section">
                <h3>📋 Список пользователей</h3>
                <div id="usersTableContainer">
                    <div class="loading-spinner"></div>
                    <p>Загрузка пользователей...</p>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(userManagementPanel);

    // Загружаем пользователей
    await loadUsers();
}

function showAddUserForm() {
    // Удаляем старую форму если есть
    const oldForm = document.getElementById('add-user-form-modal');
    if (oldForm) oldForm.remove();

    const modal = document.createElement('div');
    modal.id = 'add-user-form-modal';
    modal.className = 'modal active';
    modal.style.zIndex = '10001';
    modal.onclick = function (e) { if (e.target === this) this.remove(); };

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <button class="close-btn" onclick="document.getElementById('add-user-form-modal').remove()" style="color: white;">✕</button>
                <h2 style="color: white; font-size: 22px;">➕ Новый пользователь</h2>
            </div>
            <div class="modal-body">
                <div class="auth-form" style="box-shadow: none; padding: 0;">
                    <div class="form-group">
                        <label for="addLastName">Фамилия</label>
                        <input type="text" id="addLastName" placeholder="Введите фамилию">
                    </div>
                    <div class="form-group">
                        <label for="addFirstName">Имя</label>
                        <input type="text" id="addFirstName" placeholder="Введите имя">
                    </div>
                    <div class="form-group">
                        <label for="addPatronymic">Отчество</label>
                        <input type="text" id="addPatronymic" placeholder="Введите отчество (необязательно)">
                    </div>
                    <div class="form-group">
                        <label for="addEmail">Email</label>
                        <input type="email" id="addEmail" placeholder="Введите email">
                    </div>
                    <div class="form-group">
                        <label for="addPassword">Пароль</label>
                        <input type="password" id="addPassword" placeholder="Придумайте пароль">
                    </div>
                    <div class="form-group">
                        <label for="addRole">Роль</label>
                        <select id="addRole" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                            ${Object.entries(USER_ROLES).map(([value, info]) =>
        `<option value="${value}">${info.icon} ${info.label}</option>`
    ).join('')}
                        </select>
                    </div>
                    <button onclick="addUser()" style="margin-top: 10px;">Добавить пользователя</button>
                    <p class="form-switch" onclick="document.getElementById('add-user-form-modal').remove()">Отмена</p>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

async function addUser() {
    const data = {
        last_name: document.getElementById('addLastName').value,
        first_name: document.getElementById('addFirstName').value,
        patronymic: document.getElementById('addPatronymic').value || null,
        email: document.getElementById('addEmail').value,
        password: document.getElementById('addPassword').value
    };

    // Базовая валидация
    if (!data.last_name || !data.first_name || !data.email || !data.password) {
        alert('Заполните все обязательные поля');
        return;
    }

    if (data.password.length < 6) {
        alert('Пароль должен быть не менее 6 символов');
        return;
    }

    try {
        // 1. Регистрируем пользователя
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Ошибка: ' + error.detail);
            return;
        }

        const newUser = await response.json();

        // 2. Меняем роль на выбранную
        const selectedRole = parseInt(document.getElementById('addRole').value);
        if (selectedRole !== 0) {
            await fetch(`${API_URL}/admin/users/${newUser.id}/role`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: selectedRole })
            });
        }

        // 3. Закрываем форму и обновляем список
        document.getElementById('add-user-form-modal').remove();
        alert('✅ Пользователь добавлен');
        await loadUsers();

    } catch (error) {
        alert('Ошибка при добавлении пользователя');
    }
}

function closeUserManagement() {
    const panel = document.getElementById('user-management-panel');
    if (panel) {
        panel.remove();
    }
}

// Экспорт пользователей
async function exportUsers() {
    try {
        const response = await fetch(`${API_URL}/admin/users`);
        if (!response.ok) throw new Error('Ошибка загрузки');

        const users = await response.json();

        const exportData = users.map(u => ({
            last_name: u.last_name,
            first_name: u.first_name,
            patronymic: u.patronymic || null,
            email: u.email,
            role: u.role
        }));

        const dataStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `users_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Ошибка при экспорте пользователей');
    }
}

// Импорт пользователей
async function importUsers() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const users = JSON.parse(text);

            if (!Array.isArray(users)) {
                alert('Неверный формат файла. Ожидается массив пользователей.');
                return;
            }

            const response = await fetch(`${API_URL}/admin/users/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ users: users })
            });

            if (response.ok) {
                const result = await response.json();

                let message = `✅ Импорт завершён:\n- Добавлено: ${result.imported}\n- Пропущено (дубликаты): ${result.skipped}\n- Ошибок: ${result.errors}`;

                if (result.passwords && result.passwords.length > 0) {
                    message += '\n\n🔑 Сгенерированные пароли:\n';
                    result.passwords.forEach(p => {
                        message += `${p.email}: ${p.password}\n`;
                    });
                    message += '\n⚠️ Сохраните пароли! Они отправлены пользователям на почту.';
                }

                alert(message);
                await loadUsers();
            } else {
                alert('Ошибка при импорте');
            }

        } catch (error) {
            alert('Ошибка чтения файла. Убедитесь, что это корректный JSON.');
        }
    };

    input.click();
}

async function loadUsers() {
    try {
        console.log('Loading users from:', `${API_URL}/admin/users`);

        const response = await fetch(`${API_URL}/admin/users`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const users = await response.json();
        console.log('Users loaded:', users.length);

        const container = document.getElementById('usersTableContainer');
        if (!container) return;

        if (users.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">👥</div>
                    <h4>Пользователи не найдены</h4>
                    <p>В системе пока нет зарегистрированных пользователей</p>
                </div>
            `;
            return;
        }

        let tableHtml = `
            <div class="admin-table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Имя</th>
                            <th>Роль</th>
                            <th>Дата регистрации</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        users.forEach(user => {
            const roleInfo = getRoleInfo(user.role);
            const roleLabel = roleInfo.label;
            const roleClass = roleInfo.class;
            const fullName = `${user.last_name} ${user.first_name}`.trim();
            let createdDate = 'Неизвестно';
            if (user.created_at) {
                try {
                    const date = new Date(user.created_at);
                    if (!isNaN(date.getTime())) {
                        createdDate = date.toLocaleDateString('ru-RU');
                    }
                } catch (e) {
                    console.log('Ошибка парсинга даты:', e);
                }
            }

            tableHtml += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.email}</td>
                    <td>${fullName}</td>
                    <td><span class="role-badge ${roleClass}">${roleLabel}</span></td>
                    <td>${createdDate}</td>
                    <td>
                        <div class="actions">
                            <button class="btn-small btn-edit" onclick="toggleUserRole(${user.id}, ${user.role})">
                                🔄 Сменить роль
                            </button>
                            <button class="btn-small btn-delete" onclick="deleteUser(${user.id}, '${user.email}')">
                                🗑️ Удалить
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHtml;

    } catch (error) {
        console.error('Ошибка загрузки пользователей:', error);
        console.error('Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });

        const container = document.getElementById('usersTableContainer');
        if (container) {
            const errorMessage = error.message || 'Неизвестная ошибка';
            container.innerHTML = `
                <div class="admin-alert error">
                    <h4>❌ Ошибка загрузки пользователей</h4>
                    <p><strong>Ошибка:</strong> ${errorMessage}</p>
                    <p><strong>URL:</strong> ${API_URL}/admin/users</p>
                    <p><strong>Возможные решения:</strong></p>
                    <ul style="text-align: left; margin: 10px 0;">
                        <li>Проверьте, запущен ли бэкенд сервер на порту 8000</li>
                        <li>Убедитесь, что вы вошли как администратор</li>
                        <li>Проверьте консоль браузера для дополнительной информации</li>
                    </ul>
                </div>
            `;
        }
    }
}

async function toggleUserRole(userId, currentRole) {
    const newRole = currentRole === 1 ? 0 : 1;
    const action = newRole === 1 ? 'назначить администратором' : 'сделать пользователем';

    if (!confirm(`Вы уверены, что хотите ${action} этого пользователя?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}/role`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ role: newRole })
        });

        if (response.ok) {
            const result = await response.json();
            alert(`✅ ${result.message}`);
            await loadUsers(); // Перезагружаем список
        } else {
            const error = await response.json();
            alert(`❌ Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка изменения роли:', error);
        alert('❌ Ошибка при изменении роли пользователя');
    }
}

async function deleteUser(userId, email) {
    if (!confirm(`Вы уверены, что хотите удалить пользователя ${email}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const result = await response.json();
            alert(`✅ ${result.message}`);
            await loadUsers(); // Перезагружаем список
        } else {
            const error = await response.json();
            alert(`❌ Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка удаления пользователя:', error);
        alert('❌ Ошибка при удалении пользователя');
    }
}

// Тестирование всех внешних API
async function testAllAPIs() {
    const resultsDiv = document.createElement('div');
    resultsDiv.id = 'api-test-results';
    resultsDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
    `;

    resultsDiv.innerHTML = `
        <h2 style="color: #5A5A40; margin-bottom: 20px;">🔧 Тест внешних API</h2>
        <div id="test-results">
            <div style="text-align: center; padding: 20px;">⏳ Тестируем API...</div>
        </div>
        <button onclick="document.getElementById('api-test-results').remove()" 
                style="margin-top: 20px; padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer;">
            Закрыть
        </button>
    `;

    document.body.appendChild(resultsDiv);

    const testResults = document.getElementById('test-results');
    let results = [];

    // Тест 1: Погода (OpenMeteo)
    try {
        const response = await fetch(`${API_URL}/external/weather?lat=55.75&lon=37.61&days=3`);
        const data = await response.json();
        results.push({
            name: '🌤️ OpenMeteo (погода)',
            status: response.ok ? '✅ Работает' : '❌ Ошибка',
            details: response.ok ? `Источник: ${data.source}` : `Ошибка: ${response.status}`,
            color: response.ok ? '#4caf50' : '#f44336'
        });
    } catch (error) {
        results.push({
            name: '🌤️ OpenMeteo (погода)',
            status: '❌ Ошибка',
            details: error.message,
            color: '#f44336'
        });
    }

    // Тест 2: Поиск местоположений (2ГИС)
    try {
        const response = await fetch(`${API_URL}/external/locations/search?query=парк`);
        const data = await response.json();
        results.push({
            name: '🗺️ 2ГИС (поиск)',
            status: response.ok ? '✅ Работает' : '❌ Ошибка',
            details: response.ok ? `Найдено: ${data.locations?.length || 0} мест` : `Ошибка: ${response.status}`,
            color: response.ok ? '#4caf50' : '#f44336'
        });
    } catch (error) {
        results.push({
            name: '🗺️ 2ГИС (поиск)',
            status: '❌ Ошибка',
            details: error.message,
            color: '#f44336'
        });
    }

    // Тест 4: Экологические новости (NewsAPI)
    try {
        const response = await fetch(`${API_URL}/external/eco-news`);
        const data = await response.json();
        results.push({
            name: '📰 NewsAPI (новости)',
            status: response.ok ? '✅ Работает' : '❌ Ошибка',
            details: response.ok ? `Новостей: ${data.articles?.length || 0}` : `Ошибка: ${response.status}`,
            color: response.ok ? '#4caf50' : '#f44336'
        });
    } catch (error) {
        results.push({
            name: '📰 NewsAPI (новости)',
            status: '❌ Ошибка',
            details: error.message,
            color: '#f44336'
        });
    }

    // Отображаем результаты
    testResults.innerHTML = results.map(result => `
        <div style="margin-bottom: 15px; padding: 15px; background: ${result.color}20; border-left: 4px solid ${result.color}; border-radius: 8px;">
            <div style="font-weight: bold; color: ${result.color}; margin-bottom: 5px;">
                ${result.name}: ${result.status}
            </div>
            <div style="font-size: 14px; color: #666;">
                ${result.details}
            </div>
        </div>
    `).join('');

    // Добавляем общую статистику
    const workingCount = results.filter(r => r.status.includes('✅')).length;
    const totalCount = results.length;

    testResults.insertAdjacentHTML('beforeend', `
        <div style="margin-top: 20px; padding: 15px; background: #f5f5f0; border-radius: 8px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #5A5A40;">
                📊 Статистика: ${workingCount}/${totalCount} API работают
            </div>
            <div style="font-size: 14px; color: #666; margin-top: 5px;">
                Все API бесплатны и работают на Python 3.14
            </div>
        </div>
    `);
}

// Поиск местоположений
async function searchLocations(query) {
    if (!query.trim()) return [];

    try {
        const response = await fetch(`${API_URL}/external/locations/search?query=${encodeURIComponent(query)}&limit=5`);
        const data = await response.json();
        return data.locations || [];
    } catch (error) {
        console.error('Ошибка поиска местоположений:', error);
        return [];
    }
}

// Поиск экологических новостей
async function loadEcoNews() {
    try {
        const response = await fetch(`${API_URL}/external/eco-news`);
        const data = await response.json();

        if (data.articles && data.articles.length > 0) {
            displayEcoNews(data.articles);
        }
    } catch (error) {
        console.error('Ошибка загрузки новостей:', error);
    }
}

// Отображение экологических новостей
function displayEcoNews(articles) {
    const newsContainer = document.getElementById('newsContainer');
    if (!newsContainer) return;

    const newsHtml = `
        <div class="eco-news" style="padding: 20px; background: #f0f8f0; border-radius: 10px; border: 1px solid #4caf50;">
            <h3 style="color: #2e7d32; margin-bottom: 15px;">🌍 Экологические новости</h3>
            ${articles.map(article => `
                <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 8px;">
                    <h4 style="color: #1b5e20; margin-bottom: 8px;">${article.title}</h4>
                    <p style="color: #666; line-height: 1.6; margin-bottom: 10px;">${article.description || article.content}</p>
                    <a href="${article.url}" target="_blank" style="color: #4caf50; text-decoration: none;">Читать далее →</a>
                </div>
            `).join('')}
            <small style="color: #999; display: block; margin-top: 15px;">Источник: NewsAPI</small>
        </div>
    `;

    newsContainer.innerHTML = newsHtml;
}

function closeModal() {
    document.getElementById('holidayModal').classList.remove('active');
    currentHolidayId = null;

    // Очищаем внешние данные из модального окна
    clearExternalData();
}

// Очистка внешних данных из модального окна
function clearExternalData() {
    const modalBody = document.querySelector('.modal-body');

    // Удаляем индикатор загрузки если есть
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }

    // Находим и удаляем секции с погодой
    const sections = modalBody.querySelectorAll('div');

    sections.forEach(section => {
        const text = section.textContent;
        if (text.includes('🌤️')) {
            section.remove();
        }
    });

    // Ищем и удаляем секции по классам и тексту заголовков
    const allDivs = modalBody.querySelectorAll('div');
    allDivs.forEach(div => {
        const h3 = div.querySelector('h3');
        if (h3) {
            const text = h3.textContent;
            if (text.includes('Галерея') || text.includes('Погода')) {
                div.remove();
                return; // Выходим из forEach для этого элемента
            }
        }

        // Также удаляем по классам
        if (div.classList.contains('weather-section')) {
            div.remove();
        }
    });

    // Дополнительная очистка - ищем секции с изображениями
    const imageSections = modalBody.querySelectorAll('div img');
    imageSections.forEach(img => {
        const parentDiv = img.closest('div');
        if (parentDiv && parentDiv.querySelector('h3')?.textContent.includes('Галерея')) {
            parentDiv.remove();
        }
    });
}

async function deleteCurrentHoliday() {
    if (!currentHolidayId) return;
    if (!currentUser || currentUser.role !== 1) {
        alert('Только администратор может удалять праздники');
        return;
    }
    if (!confirm('Вы уверены, что хотите удалить этот праздник?')) return;

    try {
        await fetch(`${API_URL}/holidays/${currentHolidayId}`, { method: 'DELETE' });
        closeModal();
        loadHolidays();
    } catch (error) {
        alert('Ошибка при удалении');
    }
}

// Фильтры
function setFilter(type, value, button) {
    currentFilters[type] = value;

    button.parentElement.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
    button.classList.add('active');

    applyFilters();
}

function applyFilters() {
    currentFilters.search = document.getElementById('searchInput').value;
    loadHolidays();
}

// Закрытие модального окна по клику вне его
document.getElementById('holidayModal').addEventListener('click', function (e) {
    if (e.target === this) closeModal();
});

// Закрытие модального окна авторизации по клику вне его
document.getElementById('authModal').addEventListener('click', function (e) {
    if (e.target === this) closeAuthModal();
});




// Функции для работы с картой
let map = null;
let markers = [];
let mapUserLocation = null;

async function initializeMap() {
    const mapContainer = document.getElementById('map');
    const placeholder = document.getElementById('mapPlaceholder');

    // Инициализируем простую карту с использованием OpenStreetMap
    if (!map) {
        try {
            // Получаем геолокацию пользователя
            const position = await getCurrentPosition();
            mapUserLocation = position;

            // Создаем iframe с OpenStreetMap
            const lat = position.lat;
            const lon = position.lon;

            mapContainer.innerHTML = `
                <iframe 
                    width="100%" 
                    height="100%" 
                    frameborder="0" 
                    scrolling="no" 
                    marginheight="0" 
                    marginwidth="0" 
                    src="https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.1},${lat - 0.1},${lon + 0.1},${lat + 0.1}&layer=mapnik&marker=${lat},${lon}"
                    style="border-radius: 10px;">
                </iframe>
            `;

            // Автоматически ищем ближайшие парки
            await findNearbyParks();

        } catch (error) {
            console.error('Ошибка инициализации карты:', error);
            placeholder.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 20px;">❌</div>
                    <p>Не удалось загрузить карту</p>
                    <button onclick="initializeMap()" style="margin-top: 10px; padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer;">
                        🔄 Попробовать снова
                    </button>
                </div>
            `;
        }
    }
}

function getCurrentPosition() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    });
                },
                (error) => {
                    // Если геолокация недоступна, используем Москву по умолчанию
                    console.warn('Геолокация недоступна, используем Москву');
                    resolve({
                        lat: 55.7558,
                        lon: 37.6173
                    });
                }
            );
        } else {
            reject(new Error('Геолокация не поддерживается'));
        }
    });
}

async function searchLocation() {
    const query = document.getElementById('locationSearch').value.trim();
    if (!query) {
        alert('Введите название места для поиска');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/external/locations/search?query=${encodeURIComponent(query)}&limit=5`);
        const data = await response.json();

        if (data.locations && data.locations.length > 0) {
            displayPlaces(data.locations);

            // Обновляем карту с первым найденным местом
            const firstPlace = data.locations[0];
            updateMap(firstPlace.lat, firstPlace.lon, firstPlace.display_name);
        } else {
            document.getElementById('placesContent').innerHTML = '<p style="color: #666;">Места не найдены</p>';
        }
    } catch (error) {
        console.error('Ошибка поиска мест:', error);
        alert('Ошибка при поиске мест');
    }
}

async function findNearbyParks() {
    if (!mapUserLocation) {
        mapUserLocation = await getCurrentPosition();
    }

    try {
        const response = await fetch(`${API_URL}/external/locations/nearby?lat=${mapUserLocation.lat}&lon=${mapUserLocation.lon}&radius=5000`);
        const data = await response.json();

        if (data.locations && data.locations.length > 0) {
            displayPlaces(data.locations);

            // Добавляем маркеры на карту
            data.locations.forEach(place => {
                addMapMarker(place.lat, place.lon, place.display_name, place.class);
            });
        } else {
            document.getElementById('placesContent').innerHTML = '<p style="color: #666;">Парки и заповедники не найдены</p>';
        }
    } catch (error) {
        console.error('Ошибка поиска парков:', error);
        document.getElementById('placesContent').innerHTML = '<p style="color: #f44336;">Ошибка при поиске парков</p>';
    }
}

function displayPlaces(places) {
    const container = document.getElementById('placesContent');
    container.innerHTML = '';

    if (places.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🌳</div>
                <h4>Парки не найдены</h4>
                <p>Попробуйте увеличить радиус поиска или проверьте геолокацию</p>
            </div>
        `;
        return;
    }

    places.forEach(place => {
        const placeDiv = document.createElement('div');
        placeDiv.className = 'place-item';

        const name = place.display_name.split(',')[0];
        const fullName = place.display_name;
        const type = place.type || place.class;
        const distance = place.distance;

        placeDiv.innerHTML = `
            <div class="place-info">
                <h4>${name}</h4>
                ${fullName !== name ? `<p>${fullName}</p>` : ''}
                <div class="place-type ${type}">${getTypeLabel(type)}</div>
                ${distance ? `<span class="place-distance">${Math.round(distance)} м</span>` : ''}
            </div>
            <button class="place-btn" onclick="showOnMap(${place.lat}, ${place.lon})">📍 Показать на карте</button>
        `;
        container.appendChild(placeDiv);
    });
}

function getTypeLabel(type) {
    const labels = {
        'park': 'Парк',
        'garden': 'Сад',
        'square': 'Сквер',
        'nature_reserve': 'Заповедник',
        'forest_park': 'Лесопарк',
        'recreation': 'Рекреация'
    };
    return labels[type] || type;
}

function updateMap(lat, lon, title) {
    const mapContainer = document.getElementById('map');
    mapContainer.innerHTML = `
        <iframe 
            width="100%" 
            height="100%" 
            frameborder="0" 
            scrolling="no" 
            marginheight="0" 
            marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.05},${lat - 0.05},${lon + 0.05},${lat + 0.05}&layer=mapnik&marker=${lat},${lon}"
            style="border-radius: 10px;">
        </iframe>
    `;
}

function showOnMap(lat, lon) {
    updateMap(lat, lon);
    // Прокручиваем к карте
    document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
}

function addMapMarker(lat, lon, title, type) {
    // В будущем здесь можно добавить кастомные маркеры
    console.log(`Добавлен маркер: ${title} (${lat}, ${lon}) - ${type}`);
}

function showEditHolidayForm() {
    const holiday = allHolidays.find(h => h.id === currentHolidayId);
    if (!holiday) return;

    // Закрываем текущее модальное окно
    document.getElementById('holidayModal').classList.remove('active');

    // Удаляем старую форму если есть
    const oldForm = document.getElementById('edit-holiday-form-modal');
    if (oldForm) oldForm.remove();

    const modal = document.createElement('div');
    modal.id = 'edit-holiday-form-modal';
    modal.className = 'modal active';
    modal.style.zIndex = '2001';
    modal.onclick = function (e) { if (e.target === this) { this.remove(); document.getElementById('holidayModal').classList.add('active'); } };

    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <button class="close-btn" onclick="document.getElementById('edit-holiday-form-modal').remove(); document.getElementById('holidayModal').classList.add('active');" style="color: white;">✕</button>
                <h2 style="color: white; font-size: 22px;">✏️ Редактировать праздник</h2>
            </div>
            <div class="modal-body">
                <div class="auth-form" style="box-shadow: none; padding: 0;">
                    <div class="form-group">
                        <label for="editName">Название</label>
                        <input type="text" id="editName" value="${holiday.name.replace(/"/g, '&quot;')}">
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div class="form-group" style="flex: 1;">
                            <label for="editDay">День</label>
                            <input type="number" id="editDay" value="${holiday.day}" min="1" max="31">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label for="editMonth">Месяц</label>
                            <select id="editMonth" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                                ${monthNames.map((m, i) => `<option value="${i}" ${i === holiday.month ? 'selected' : ''}>${m}</option>`).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="editType">Тип</label>
                        <select id="editType" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                            <option value="eco" ${holiday.type === 'eco' ? 'selected' : ''}>🌿 Экологический</option>
                            <option value="national" ${holiday.type === 'national' ? 'selected' : ''}>🇷🇺 Национальный</option>
                            <option value="world" ${holiday.type === 'world' ? 'selected' : ''}>🌍 Мировой</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editRegion">Регион</label>
                        <select id="editRegion" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">
                            <option value="russia" ${holiday.region === 'russia' ? 'selected' : ''}>🇷🇺 Россия</option>
                            <option value="world" ${holiday.region === 'world' ? 'selected' : ''}>🌍 Весь мир</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="editDescription">Описание</label>
                        <textarea id="editDescription" rows="4" style="width: 100%; padding: 15px 20px; border: 2px solid #e0e0d0; border-radius: 15px; font-size: 16px; outline: none;">${holiday.description.replace(/"/g, '&quot;')}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="editEvents">Мероприятия (через запятую)</label>
                        <input type="text" id="editEvents" value="${(holiday.events || []).join(', ').replace(/"/g, '&quot;')}">
                    </div>
                    <div class="form-group">
                        <label for="editWikiUrl">Ссылка на Википедию</label>
                        <input type="url" id="editWikiUrl" value="${holiday.wikipedia_url || ''}">
                    </div>
                    <button onclick="updateHoliday(${holiday.id})" style="margin-top: 10px;">💾 Сохранить изменения</button>
                    <p class="form-switch" onclick="document.getElementById('edit-holiday-form-modal').remove(); document.getElementById('holidayModal').classList.add('active');">Отмена</p>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

async function updateHoliday(holidayId) {
    const events = document.getElementById('editEvents').value
        .split(',')
        .map(e => e.trim())
        .filter(e => e);

    const data = {
        name: document.getElementById('editName').value,
        day: parseInt(document.getElementById('editDay').value),
        month: parseInt(document.getElementById('editMonth').value),
        type: document.getElementById('editType').value,
        region: document.getElementById('editRegion').value,
        description: document.getElementById('editDescription').value,
        events: events,
        wikipedia_url: document.getElementById('editWikiUrl').value
    };

    // Проверка на дубликат (исключая текущий праздник)
    const isDuplicate = await checkHolidayDuplicate(data.name, data.day, data.month, holidayId);
    if (isDuplicate) {
        alert('⚠️ Праздник с таким названием уже существует!');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/holidays/${holidayId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            document.getElementById('edit-holiday-form-modal').remove();
            await loadHolidays();
            alert('✅ Праздник обновлён');
        } else {
            const error = await response.json();
            alert('Ошибка: ' + error.detail);
        }
    } catch (error) {
        alert('Ошибка при обновлении праздника');
    }
}

// Проверка на дубликаты праздников
async function checkHolidayDuplicate(name, day, month, excludeId = null) {
    // excludId — ID праздника, который исключаем из проверки (при редактировании)
    const duplicate = allHolidays.find(h =>
        h.name.toLowerCase() === name.toLowerCase() &&
        h.id !== excludeId
    );
    return !!duplicate;
}

// Первая загрузка
getUserLocation();
initMonthSelect();
loadHolidays();