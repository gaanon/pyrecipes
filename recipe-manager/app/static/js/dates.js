// Date helpers for the meal planner; loaded by the page before planner.js, and by the tests in Node.
(function (exports) {
    function getWeekRange(date) {
        const start = new Date(date);
        const day = start.getDay();
        const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Adjust to Monday as start of week
        start.setDate(diff);
        const end = new Date(start);
        end.setDate(start.getDate() + 6);
        return { start, end };
    }

    // "YYYY-MM-DD" for the local calendar day (toISOString would give the UTC day,
    // which is off by one near midnight)
    function formatDate(date) {
        const pad = (n) => String(n).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    }

    exports.getWeekRange = getWeekRange;
    exports.formatDate = formatDate;
})(typeof module !== 'undefined' ? module.exports : (window.PlannerDates = {}));
