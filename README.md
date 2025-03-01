# PC Part Picker – Automated PC Build Recommender

## Project Overview
PC Part Picker is a web-based tool designed to help users build their ideal PC by recommending the best components currently on sale across multiple e-commerce websites. The tool gathers, filters, and presents the most suitable PC components based on user preferences and budget, providing a seamless experience for users looking to build or upgrade their PCs.

## Features
- **Web Scraping**: Collects data from multiple e-commerce websites to get the best deals on PC components.
- **User Customization**: Users can specify their preferences (e.g., purpose of the PC, budget, brand preferences) for more tailored recommendations.
- **Real-time Updates**: The tool regularly fetches new data to ensure users are always presented with up-to-date pricing and availability.
- **PC Build Recommendations**: Based on user inputs, it suggests the best components (CPU, GPU, motherboard, RAM, etc.) optimized for the given criteria.
- **User-friendly Interface**: An intuitive frontend allows users to easily input their preferences and receive recommendations.

## Tech Stack
- **Frontend**: React
- **Backend**: Node.js
- **Database**: MySQL
- **Web Scraping**: Python (BeautifulSoup, Requests)
- **Data Filtering & Parsing**: Python (pandas, regex)
- **Recommendation System**: Custom algorithm based on user input and component features
