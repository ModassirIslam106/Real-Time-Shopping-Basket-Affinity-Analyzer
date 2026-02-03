# Real-Time-Shopping-Basket-Affinity-Analyzer

📌 Project Overview

This project is a Shopping Basket Affinity Analyzer built as part of a hackathon.
The goal of the project is to identify products that are frequently purchased together by customers using association rule mining techniques.

Instead of traditional machine learning prediction, this project focuses on pattern discovery from transactional retail data to generate insights such as:

“Customers who buy Product A are also likely to buy Product B.”

The project is designed to be interactive, explainable, and scalable, with a web-based UI built using Streamlit.


## Problem Statement
🎯 Problem Statement

Retailers want to improve:

Cross-selling

Product placement

Recommendation systems

However, analyzing large volumes of transactional data to discover meaningful product associations is challenging.

Objective:
Build a system that analyzes shopping basket data and identifies strong product affinities using metrics like support, confidence, and lift.



## Solution Overview
🧠 Solution Approach (What We Did)

The project is divided into four clear stages:

1️⃣ Synthetic Data Generation

Since real retail data was not available, we generated realistic synthetic transaction data using a category-driven probabilistic approach.

Generated datasets:

products.csv → Product catalog

store_sales_header.csv → Transaction metadata

store_sales_line_items.csv → Product-level purchase details

This ensures:

Realistic co-purchase patterns

Meaningful affinity scores

Full control over data size and behavior



## Data Description and Preparation
2️⃣ Data Preparation & Basket Creation

Transactional data is transformed into shopping baskets, where each transaction is represented as a list of purchased products:

Transaction T001 → [Milk, Bread, Butter]

This format is essential for association rule mining.



3️⃣ Affinity Model (Association Rule Mining)

Instead of training a predictive ML model, we built an affinity analysis pipeline that:
Generates all unique product pairs
Computes key metrics:
Support – How often two products are bought together
Confidence – Likelihood of buying product B given product A
Lift – Strength of association (>1 indicates strong affinity)
These metrics help quantify how meaningful a product relationship is.





4️⃣ Interactive Streamlit Web App

The final output is an interactive Streamlit dashboard that allows users to:

Adjust minimum support and confidence thresholds

Select top-K product affinities

View results instantly in a table

Understand business insights visually and intuitively

This makes the project demo-ready for hackathons and presentations.



Presented by Modassir