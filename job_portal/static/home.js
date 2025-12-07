document.getElementById('view-more-btn').addEventListener('click', function() {
    // Add more categories dynamically
    const categories = [
        { name: 'Teacher', icon: 'fa fa-user-graduate', jobs: '100+' },
        { name: 'Content Writer', icon: 'fa fa-pencil-alt', jobs: '200+' },
        { name: 'Customer Support', icon: 'fa fa-headset', jobs: '250+' },
        { name: 'Human Resources', icon: 'fa fa-users', jobs: '300+' },
        { name: 'Automobile', icon: 'fa fa-car', jobs: '400+' },
        { name: 'Logistics / Delivery', icon: 'fa fa-truck', jobs: '1k+' },
    ];

    const categoryGrid = document.getElementById('category-grid');
    const existingCardsCount = categoryGrid.children.length;

    const colors = [
        { color: '#ff6347', background: '#fff3f0' },
        { color: '#9370db', background: '#f5f0ff' },
        { color: '#ffa500', background: '#fff7e6' },
        { color: '#00ced1', background: '#e5ffff' },
        { color: '#32cd32', background: '#f3fff3' },
        { color: '#ff4500', background: '#fff0eb' },
    ];

    categories.forEach((category, index) => {
        const nthChild = existingCardsCount + index + 1; // Calculate the position of the new card
        const colorIndex = nthChild - 9; // Map nth-child to colors array (starts at 9)

        const card = document.createElement('div');
        card.classList.add('explore__card');

        card.innerHTML = `
            <span><i class="${category.icon}"></i></span>
            <h4>${category.name}</h4>
            <p>${category.jobs} job openings</p>
        `;

        // Apply colors only for cards 9 to 14
        if (colorIndex >= 0 && colorIndex < colors.length) {
            const color = colors[colorIndex];
            card.querySelector('span').style.color = color.color;
            card.querySelector('span').style.backgroundColor = color.background;
        }

        categoryGrid.appendChild(card);
    });

    // Center the "View More" and "View Less" buttons
    const exploreBtn = document.querySelector('.explore__btn');
    exploreBtn.style.display = 'flex';
    exploreBtn.style.justifyContent = 'center';
    exploreBtn.style.alignItems = 'center';

    // Hide the "View More" button and show the "View Less" button
    document.getElementById('view-more-btn').style.display = 'none';
    document.getElementById('view-less-btn').style.display = 'block';
});

document.getElementById('view-less-btn').addEventListener('click', function() {
    // Hide the extra categories and show only the first 8
    const categoryGrid = document.getElementById('category-grid');
    
    // Remove the extra categories added dynamically
    const allCards = categoryGrid.getElementsByClassName('explore__card');
    while (allCards.length > 8) {
        categoryGrid.removeChild(allCards[8]); // Remove cards after the first 8
    }

    // Center the "View More" and "View Less" buttons
    const exploreBtn = document.querySelector('.explore__btn');
    exploreBtn.style.display = 'flex';
    exploreBtn.style.justifyContent = 'center';
    exploreBtn.style.alignItems = 'center';

    // Show the "View More" button and hide the "View Less" button
    document.getElementById('view-more-btn').style.display = 'block';
    document.getElementById('view-less-btn').style.display = 'none';
});
