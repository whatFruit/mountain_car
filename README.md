# Mountain Car RL
##### Author: Matthew Atteberry

### Overview:
The Mountain Car problem is a classic machine learning task. The set-up is a 'car' (in this excerise, a simple ball), that can accelerate left, right, or stay in neutral (its **action**). This car starts at the bottom of a valley that it can not simply accelerate out of, but must build momentum by going up left and right slopes in order to climb the 'mountain'. Machine learning is used to formulate a policy based on the car's position and velocity (its **state**) that directs the car out of the valley.

#### Dependencies
- [Pymunk](https://github.com/viblo/pymunk)
- [Pygame](https://github.com/pygame/pygame)

#### status: WIP
- [x] Setup Basic Pygame/Pymunk scene and loop
- [ ] Setup Mountain and Car sprites/physics objects
- [ ] Provide Access to cars state and actions as an RL agent
- [ ] Design and implement Value Approximation RL methods
- [ ] Hook up RL training method with car agent
- [ ] Design and implement a visualization of the car agent's policy 