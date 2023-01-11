---
title: darkfi lottery simulation
author: ertosns
date: 11/1/2023
---

simulate darkfi consensus lottery with a discrete controler

# discrete pid controller.
control lottery f tunning paramter

$k_1 = k_p + K_i + K_d$
$k_2 = -K_p -2K_d$
$k_3 = K_d$
$$f[k] = f[k-1] + K_1e[k] + K_2e[k-1] + K_3e[k-2]$$

# simulation criterion
find $K_p$, $k_i$, $K_d$ for highest accuracy running the simulation on N trials, of random number of nodes, starting with random airdrop (that all sum to total network stake), running for random runing_time.

![alt text](https://github.com/ertosns/lotterysim/blob/master/heuristics.png?raw=true)

notice that best parameters are spread out in the search space, picking the highest of which, and running the simulation, running for 600 slots.

![alt text](https://github.com/ertosns/lotterysim/blob/master/f_history_processed.png?raw=true)

# comparing range of target values between

notice below that both y,T in the pallas field, and simulation have same range.

![alt text](https://github.com/ertosns/lotterysim/blob/master/lottery_dist.png?raw=true)


# conclusion

using discrete controller the lottery accuracy > 33% with randomized number of nodes, and randomized relative stake.
can be coupled with khonsu[^1] to achieve 100% accuracy and instant finality.

[^1]: https://github.com/ertosns/thunderbolt
