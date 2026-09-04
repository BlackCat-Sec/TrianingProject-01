# Data Cleaning

## Overview

Data Cleaning is an important step in the RAG (Retrieval-Augmented Generation) pipeline.

This module cleans and prepares the raw data received from the Data Loading module before it is passed to the Text Chunking module.

## Objectives

- Remove unnecessary spaces and blank lines.
- Remove unwanted characters.
- Remove duplicate content.
- Check for empty or invalid data.
- Prepare clean data for text chunking.

## Workflow

```text
Data Loading
     ↓
Raw Data
     ↓
Data Cleaning
     ↓
Clean Data
     ↓
Text Chunking
