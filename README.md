# OrganLink – AI-Powered Organ Donation and Compatibility Prediction Platform

OrganLink is an AI-powered organ donation platform designed to bridge the gap between organ donors and recipients through technology. The platform aims to simplify donor and recipient registration, assist doctors in identifying potential organ compatibility, and promote awareness about organ donation.

The system integrates Machine Learning for compatibility prediction and provides a centralized platform for managing donor and recipient information.

## Project Overview

Organ donation plays a crucial role in saving lives, but connecting suitable donors with recipients can be challenging.

OrganLink aims to address this challenge by providing a centralized digital platform with role-based access for donors, recipients, and doctors.

The platform includes an AI-assisted compatibility prediction module that analyzes relevant medical information to estimate compatibility between donors and recipients.

## Objectives

- Develop a centralized organ donation platform.
- Provide donor and recipient registration.
- Implement AI-assisted organ compatibility prediction.
- Help doctors identify and review potentially compatible recipients.
- Provide a doctor dashboard for managing medical information.
- Promote organ donation awareness.
- Analyze public awareness through survey data and visualizations.
- Maintain secure, role-based access to the platform.

## Key Features

### 1. Donor Registration
- Register as an organ donor.
- Maintain donor information.
- Store relevant medical details.

### 2. Recipient Registration
- Register as an organ recipient.
- Maintain recipient information.
- Store required medical details.

### 3. Doctor Dashboard
- Dedicated dashboard for doctors.
- Access donor and recipient information.
- Enter and manage relevant medical test values.
- View AI-assisted compatibility results.

### 4. AI-Based Compatibility Prediction
- Analyze relevant donor and recipient medical attributes.
- Estimate compatibility using Machine Learning.
- Generate compatibility scores.
- Help doctors review and prioritize potential matches.

### 5. Organ Donation Awareness
- Provide educational information about organ donation.
- Promote public awareness.
- Explain the importance of organ donation.

### 6. Survey Analysis
- Collect public awareness data using Google Forms.
- Analyze awareness levels and willingness to donate.
- Visualize survey responses and findings.

### 7. Role-Based Authentication
- Separate login access for donors, recipients, and doctors.
- Manage user information through a centralized database.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development and Machine Learning |
| Flask | Web application framework |
| MySQL | Database management |
| HTML5 | Frontend structure |
| CSS3 | Styling and UI design |
| Pandas | Data processing and analysis |
| Scikit-learn | Machine Learning |
| NumPy | Numerical computations |
| Matplotlib | Data visualization |

## Machine Learning Approach

The project uses Machine Learning techniques to assist in estimating organ compatibility between donors and recipients.

The proposed workflow includes:

1. Collecting relevant donor and recipient medical information.
2. Processing and preparing medical attributes.
3. Analyzing relevant compatibility factors.
4. Applying Machine Learning algorithms.
5. Generating compatibility predictions and scores.
6. Presenting results through the doctor dashboard.

**Note:** Compatibility predictions are intended as decision-support information. They are not a substitute for clinical evaluation, transplant-team decisions, or official organ allocation procedures.

## System Architecture

The platform follows a web-based architecture consisting of:

- **Frontend:** HTML and CSS.
- **Backend:** Python and Flask.
- **Database:** MySQL.
- **Machine Learning:** Python, Pandas and Scikit-learn.
- **User Roles:** Donor, Recipient and Doctor.


## Project Structure

```text
OrganLink/
│
├── app.py
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│   ├── donor.html
│   ├── recipient.html
│   ├── hospital.html
│   ├── add_hospital.html
│   ├── edit_profile.html
│   ├── profile.html
│   ├── organ_registration.html
│   ├── organ_request.html
│   ├── donation_status.html
│   ├── request_status.html
│   ├── ai_compatibility.html
│   ├── hospital_ai_matching.html
│   ├── matching_results.html
│   ├── hospital_add_recipient.html
│   ├── hospital_reports.html
│   ├── medical_reports.html
│   ├── verify_donors.html
│   ├── verify_recipients.html
│   ├── view_donors.html
│   ├── view_recipients.html
│   ├── view_hospitals.html
│   ├── view_users.html
│   ├── awareness.html
│   ├── waiting_list.html
│   ├── system.html
│   └── terms.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements.txt
│
└── README.md
```


*The structure above is a suggested organization; adjust it to match the actual files in your repository.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/OrganLink-Organ-Donation-Platform.git
```

### 2. Navigate to the Project Directory

```bash
cd OrganLink-Organ-Donation-Platform
```

### 3. Install Dependencies

```bash
pip install flask mysql-connector-python pandas numpy scikit-learn matplotlib
```

### 4. Configure MySQL

- Install MySQL and MySQL Workbench.
- Create a database named `organlink`.
- Configure the database connection details in your Flask application.
- Create the required database tables.

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000/
```

## Future Enhancements

- Improve Machine Learning compatibility prediction.
- Integrate secure medical report uploads.
- Implement advanced donor-recipient matching.
- Add notification and communication features.
- Improve dashboard analytics.
- Integrate additional medical compatibility parameters.
- Enhance data security and privacy.

## Disclaimer

OrganLink is an academic project developed for educational and research purposes. Its AI-assisted compatibility predictions are not clinically validated and must not be used independently to determine transplant eligibility or organ allocation. All medical decisions must be made by qualified transplant professionals following applicable medical and legal guidelines.

---

## Developed By

**OrganLink – AI-Powered Organ Donation and Compatibility Prediction Platform**

Romil Atmaramani 
