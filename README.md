<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Django Job Portal - Project Preview</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    /* Global Styles */
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
    body { background-color: #f9fafb; color: #333; line-height: 1.6; }
    a { text-decoration: none; color: inherit; }
    img { max-width: 100%; display: block; }
    .container { width: 90%; max-width: 1200px; margin: auto; padding: 20px 0; }
    
    /* Header */
    header { text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 0 0 20px 20px; }
    header h1 { font-size: 3rem; margin-bottom: 10px; }
    header p { font-size: 1.2rem; }

    /* Section Titles */
    h2 { color: #4b5563; font-size: 2rem; margin-bottom: 15px; text-align: center; }
    h3 { color: #6b7280; font-size: 1.5rem; margin-bottom: 10px; }

    /* Cards */
    .card { background: white; border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); padding: 20px; margin: 20px 0; }
    .card img { border-radius: 20px; margin-top: 10px; }

    /* Features Section */
    .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
    .feature { background: #fff; border-radius: 15px; padding: 20px; text-align: center; transition: transform 0.3s ease; cursor: pointer; }
    .feature:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); }

    /* Buttons */
    .btn { display: inline-block; padding: 10px 20px; margin-top: 15px; border-radius: 10px; background: #667eea; color: white; font-weight: 600; transition: 0.3s ease; }
    .btn:hover { background: #764ba2; }

    /* Footer */
    footer { text-align: center; padding: 30px 20px; color: #6b7280; font-size: 0.9rem; }

    /* Animations */
    .fade-in { opacity: 0; transform: translateY(20px); transition: all 0.6s ease-out; }
    .fade-in.visible { opacity: 1; transform: translateY(0); }
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <h1>Django Job Portal</h1>
    <p>Modern Job Portal Web Application with ATS-based recommendations and Analytics</p>
  </header>

  <!-- About Section -->
  <section class="container">
    <div class="card fade-in">
      <h2>Project Overview</h2>
      <p>
        A full-featured Job Portal built using Django, designed for job seekers and recruiters. 
        Users can search and apply for jobs, track applications, manage profiles, and view ATS score–based recommendations.
      </p>
    </div>
  </section>

  <!-- Features Section -->
  <section class="container">
    <h2>🌟 Features</h2>
    <div class="features">
      <div class="feature fade-in">
        <h3>👤 User Features</h3>
        <ul>
          <li>Create account, login, logout</li>
          <li>Update profile, skills, resume</li>
          <li>ATS Score calculation & job recommendations</li>
          <li>Apply to jobs & track status</li>
          <li>Save favorite jobs</li>
        </ul>
      </div>
      <div class="feature fade-in">
        <h3>🛠️ Admin/Recruiter Features</h3>
        <ul>
          <li>Add, edit, delete jobs</li>
          <li>View applicants</li>
          <li>Manage job categories</li>
          <li>Post jobs for users to apply</li>
        </ul>
      </div>
      <div class="feature fade-in">
        <h3>💡 Technical Highlights</h3>
        <ul>
          <li>Django custom authentication</li>
          <li>Clean folder structure (users, jobs, dashboard)</li>
          <li>Bootstrap/HTML/CSS frontend</li>
          <li>ORM-based queries & ATS logic</li>
          <li>Fully responsive UI</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Screenshots Section -->
  <section class="container">
    <h2>✨ UI Screenshots</h2>

    <div class="card fade-in">
      <h3>🏠 Home Page</h3>
      <img src="screenshots/home.jpg" alt="Home Page">
    </div>

    <div class="card fade-in">
      <h3>🔐 Login Page</h3>
      <img src="screenshots/login.jpg" alt="Login Page">
    </div>

    <div class="card fade-in">
      <h3>📊 Dashboard</h3>
      <img src="screenshots/dashboard.jpg" alt="Dashboard">
    </div>
  </section>

  <!-- Footer -->
  <footer>
    &copy; 2025 Django Job Portal. Designed with ❤️ by Tuhin Saha
  </footer>

  <!-- JavaScript for Scroll Animations -->
  <script>
    const faders = document.querySelectorAll('.fade-in');

    const appearOptions = {
      threshold: 0.2
    };

    const appearOnScroll = new IntersectionObserver(function(entries, observer) {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      });
    }, appearOptions);

    faders.forEach(fader => {
      appearOnScroll.observe(fader);
    });
  </script>

</body>
</html>
