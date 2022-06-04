# Snowbudget

I'm developing this program to more easily keep track of my expenses. As a
recent college graduate taking on a full-time position, I felt this is important
to get right. And what better way than to write a program!

<img src="root/assets/logo.png" width=256>

## Installation 

To run this app:
1. Fork it
2. Install Docker
3. Run `docker compose up -d` 
4. Navigate to http://localhost:8080.

## Contributors

Thanks a lot to Abhishek Sathiabalan for taking interest in the project and
integrating Docker to make for better deployment!

## TODO
0. Add credentials manager UI
1. Add code that goes out and gets all transactions from a particular financial institution in a month (?); how would they get categorized ? It would be a mix of expenses and income.
2. Change add transactions so a user can select the date when a transaction occured
3. Add an option for savings/budget.json to allow savings rate to be computed against your gross income
4. Is there a way to delete or otherwise edit transactions ? 
5. Figure out why chart doesn't work on Docker but it does for Connor.