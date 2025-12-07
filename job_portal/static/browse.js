document.addEventListener('DOMContentLoaded', function () {
    const paginationLinks = document.querySelectorAll('.pagination a');
    const jobContainer = document.querySelector('.row.row-cols-1');

    paginationLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const url = this.href;

            fetch(url)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newJobs = doc.querySelector('.row.row-cols-1').innerHTML;
                    const newPagination = doc.querySelector('.pagination').outerHTML;

                    jobContainer.innerHTML = newJobs;
                    document.querySelector('.pagination').outerHTML = newPagination;
                })
                .catch(error => console.error('Error loading new jobs:', error));
        });
    });
});
