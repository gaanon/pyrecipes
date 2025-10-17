document.addEventListener('DOMContentLoaded', function () {
    // --- Planner Panel Elements ---
    const togglePlannerBtn = document.getElementById('toggle-planner-btn');
    const plannerPanel = document.getElementById('planner-panel');
    const daysList = document.getElementById('planner-days-list');
    const mealsList = document.getElementById('planner-meals-list');
    const weekDisplay = document.getElementById('week-display');
    const prevWeekBtn = document.getElementById('prev-week-btn');
    const nextWeekBtn = document.getElementById('next-week-btn');
    const selectedDayDisplay = document.getElementById('selected-day-display');
    const addCustomMealBtn = document.getElementById('add-custom-meal-btn');
    const customMealNameInput = document.getElementById('custom-meal-name');

    // --- Add to Plan Modal Elements ---
    const addToPlanModalEl = document.getElementById('addToPlanModal');
    const addToPlanModal = new bootstrap.Modal(addToPlanModalEl);
    const modalWeekDisplay = document.getElementById('modal-week-display');
    const modalPrevWeekBtn = document.getElementById('modal-prev-week-btn');
    const modalNextWeekBtn = document.getElementById('modal-next-week-btn');
    const modalDaysContainer = document.getElementById('modal-days-container');
    const modalTitle = document.getElementById('addToPlanModalLabel');

    // --- State ---
    let plannerCurrentDate = new Date();
    let modalCurrentDate = new Date();
    let weekData = [];
    let selectedPlannerDate = new Date().toISOString().split('T')[0];
    let recipeToAdd = null;

    // --- Utility Functions ---
    function getWeekRange(date) {
        const start = new Date(date);
        const day = start.getDay();
        const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Adjust to Monday as start of week
        start.setDate(diff);
        const end = new Date(start);
        end.setDate(start.getDate() + 6);
        return { start, end };
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    // --- Planner Panel Logic ---
    function togglePlanner() {
        document.body.classList.toggle('planner-open');
        plannerPanel.classList.toggle('show');
        if (plannerPanel.classList.contains('show')) {
            togglePlannerBtn.textContent = 'Hide Planner';
            loadPlannerWeek(plannerCurrentDate);
        } else {
            togglePlannerBtn.textContent = 'Show Planner';
        }
    }

    async function loadPlannerWeek(date) {
        const { start, end } = getWeekRange(date);
        weekDisplay.textContent = `${start.toLocaleDateString()} - ${end.toLocaleDateString()}`;
        try {
            const response = await fetch(`/api/meal-plan?start_date=${formatDate(start)}&end_date=${formatDate(end)}`);
            if (!response.ok) throw new Error('Failed to fetch meal plan');
            weekData = await response.json();
            renderPlannerWeek(start);
            renderMealsForDay(selectedPlannerDate);
        } catch (error) {
            console.error("Error loading planner data:", error);
            daysList.innerHTML = '<li class="list-group-item text-danger">Could not load week data.</li>';
        }
    }

    function renderPlannerWeek(startDate) {
        daysList.innerHTML = '';
        for (let i = 0; i < 7; i++) {
            const day = new Date(startDate);
            day.setDate(day.getDate() + i);
            const dayStr = formatDate(day);
            const mealsForDay = weekData.filter(meal => meal.plan_date === dayStr);
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.dataset.date = dayStr;
            let content = `<span><small class="text-muted">${day.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()}</small> <strong>${day.getDate()}</strong></span>`;
            if (mealsForDay.length > 0) {
                content += `<span class="badge bg-primary rounded-pill">${mealsForDay.length}</span>`;
            }
            li.innerHTML = content;
            if (dayStr === selectedPlannerDate) {
                li.classList.add('active');
                selectedDayDisplay.textContent = day.toLocaleDateString('en-US', { weekday: 'long' });
            }
            li.addEventListener('click', () => {
                selectedPlannerDate = dayStr;
                document.querySelectorAll('#planner-days-list .list-group-item').forEach(item => item.classList.remove('active'));
                li.classList.add('active');
                selectedDayDisplay.textContent = day.toLocaleDateString('en-US', { weekday: 'long' });
                renderMealsForDay(dayStr);
            });
            daysList.appendChild(li);
        }
    }

    function renderMealsForDay(dateStr) {
        mealsList.innerHTML = '';
        const mealsForDay = weekData.filter(meal => meal.plan_date === dateStr);
        if (mealsForDay.length === 0) {
            mealsList.innerHTML = '<li class="list-group-item text-muted">No meals planned.</li>';
            return;
        }
        mealsForDay.forEach(meal => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            let mealName = meal.custom_meal_name;
            if (meal.recipe) {
                mealName = `<a href="/recipe/${meal.recipe.id}">${meal.recipe.name}</a>`;
            }
            li.innerHTML = `<span>${mealName}</span><button class="btn btn-sm btn-outline-danger" data-meal-id="${meal.id}">&times;</button>`;
            mealsList.appendChild(li);
        });
    }

    // --- Add to Plan Modal Logic ---
    function renderModalWeek(date) {
        const { start, end } = getWeekRange(date);
        modalWeekDisplay.textContent = `${start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
        modalDaysContainer.innerHTML = '';
        for (let i = 0; i < 7; i++) {
            const day = new Date(start);
            day.setDate(day.getDate() + i);
            const dayStr = formatDate(day);
            const dayDiv = document.createElement('div');
            dayDiv.className = 'col';
            dayDiv.innerHTML = `<div class="day p-2" data-date="${dayStr}">
                                    <div>${day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                                    <strong>${day.getDate()}</strong>
                                </div>`;
            dayDiv.addEventListener('click', () => addRecipeToPlan(dayStr));
            modalDaysContainer.appendChild(dayDiv);
        }
    }

    async function addRecipeToPlan(dateStr) {
        if (!recipeToAdd) return;
        const mealData = {
            plan_date: dateStr,
            recipe_id: recipeToAdd.id
        };
        try {
            const response = await fetch('/api/meal-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(mealData)
            });
            if (!response.ok) throw new Error('Failed to add recipe to meal plan');
            addToPlanModal.hide();
            if (plannerPanel.classList.contains('show')) {
                loadPlannerWeek(plannerCurrentDate);
            }
        } catch (error) {
            console.error("Error adding recipe to meal plan:", error);
        }
    }

    // --- Event Listeners ---
    if (togglePlannerBtn) {
        togglePlannerBtn.addEventListener('click', togglePlanner);
    }

    document.addEventListener('click', function (event) {
        const isClickInsidePlanner = plannerPanel.contains(event.target);
        const isClickOnToggleBtn = togglePlannerBtn.contains(event.target);
        if (plannerPanel.classList.contains('show') && !isClickInsidePlanner && !isClickOnToggleBtn) {
            togglePlanner();
        }
    });

    prevWeekBtn.addEventListener('click', () => {
        plannerCurrentDate.setDate(plannerCurrentDate.getDate() - 7);
        loadPlannerWeek(plannerCurrentDate);
    });

    nextWeekBtn.addEventListener('click', () => {
        plannerCurrentDate.setDate(plannerCurrentDate.getDate() + 7);
        loadPlannerWeek(plannerCurrentDate);
    });

    addCustomMealBtn.addEventListener('click', async () => {
        const mealName = customMealNameInput.value.trim();
        if (!mealName) return;
        const mealData = { plan_date: selectedPlannerDate, custom_meal_name: mealName };
        try {
            const response = await fetch('/api/meal-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(mealData)
            });
            if (!response.ok) throw new Error('Failed to add meal');
            customMealNameInput.value = '';
            loadPlannerWeek(plannerCurrentDate);
        } catch (error) {
            console.error("Error adding custom meal:", error);
        }
    });

    mealsList.addEventListener('click', async (e) => {
        if (e.target.matches('.btn-outline-danger')) {
            const mealId = e.target.dataset.mealId;
            if (!mealId) return;
            try {
                const response = await fetch(`/api/meal-plan/${mealId}`, { method: 'DELETE' });
                if (!response.ok) throw new Error('Failed to delete meal');
                loadPlannerWeek(plannerCurrentDate);
            } catch (error) {
                console.error("Error deleting meal:", error);
            }
        }
    });

    document.addEventListener('click', (e) => {
        if (e.target.matches('.add-to-planner-btn')) {
            const card = e.target.closest('.recipe-card');
            const recipeId = e.target.dataset.recipeId;
            const recipeName = card.querySelector('.card-title').textContent;
            recipeToAdd = { id: parseInt(recipeId), name: recipeName };
            modalTitle.textContent = `Add "${recipeName}" to Meal Plan`;
            renderModalWeek(modalCurrentDate);
            addToPlanModal.show();
        }
    });

    modalPrevWeekBtn.addEventListener('click', () => {
        modalCurrentDate.setDate(modalCurrentDate.getDate() - 7);
        renderModalWeek(modalCurrentDate);
    });

    modalNextWeekBtn.addEventListener('click', () => {
        modalCurrentDate.setDate(modalCurrentDate.getDate() + 7);
        renderModalWeek(modalCurrentDate);
    });
});