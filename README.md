# survival_of_the_fittest

## A survival analysis of A rated restaurants in NYC

This analysis looks specifically on restaurants which originally achieved an A rating as their initial grade from the Department of Health with the aim of understanding how long such restaurants on average retain their grade.

Interestly, the majority of ratings losses appear distributed in roughly 6 month cycles, likely due to the cadence of the inspection cycle as shown in the distribution of grade changes from A to a lesser grade by days from the initial inspection date.

![alt tag](https://github.com/andrewwowens/survival_of_the_fittest/blob/master/distribution_of_ratings_losses.png)

The initial results show that restaurants in the Bronx diverge from the rest of the NYC boroughs in their ability to retain their A rating after roughly a year from their initial inspection dates.

![alt tag](https://github.com/andrewwowens/survival_of_the_fittest/blob/master/Lifespans%20of%20A%20rated%20restaurant%20by%20NYC%20borough.png)

Overall, the other four boroughs reveal that restaurants are usually only at a 14% likelihood to lose their rating after a roughly 2 year period.

![alt tag](https://github.com/andrewwowens/survival_of_the_fittest/blob/master/Hazard%20functions%20of%20A%20rated%20restaurant%20by%20NYC%20borough.png)
