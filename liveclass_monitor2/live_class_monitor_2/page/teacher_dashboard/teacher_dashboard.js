console.log("✔ teacher_dashboard.js LOADED");

// Desk pages use this API
frappe.pages['teacher_dashboard'].on_page_load = function(wrapper) {
    console.log("✔ Teacher Dashboard page load");

    // Create a page container
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Teacher Dashboard',
        single_column: true
    });

    // Load HTML into the page
    $(wrapper).find('.layout-main').html(
        frappe.render_template('teacher_dashboard')
    );

    console.log("✔ HTML Rendered Successfully");
};

// Socket connection test
frappe.realtime.on("student_status_change", data => {
    console.log("REALTIME EVENT RECEIVED:", data);
});

