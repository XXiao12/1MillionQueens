import numpy as np 
from progressbar import update_progress

class board:
    def __init__(self, size=8, C1=0.45, C2=32, randinit=True, threshold=20,with_progressbar_when_initializing=False):
        self.N = size 
        ### TODO: dtype reinitialize, reduce memory
        self.bd = np.arange(self.N, dtype=np.uint32) ### because len(bin(1000000)) < 32

        self.dp = np.zeros(2*self.N, dtype=np.uint32) # [2 .. 2*N-2]
        # if use greedy init, dtype can be set uint8 or even smaller
        self.dn = np.zeros(2*self.N, dtype=np.uint32) # careful with the indexing
        self.attack = []
        # because we use index starting from 0, so the attack matrix is initialized with -1 instead of 0 (0 means column one)
        self.limit = 0
        self.collisions = 1
        self.number_of_attacks = 0
        self.loopcount = 0
        self.C1 = C1
        self.C2 = C2
        if randinit:
            self.randinit()  
        else:
            self.threshold = threshold
            self.with_progressbar_when_initializing = with_progressbar_when_initializing
            self.greedyinit()
        self.iter_num = 0
        self._old = 0
        self._new = 0
        
        
    def printall(self,bd=True,attack=True):
        if self.N > 10:
            print("size {} is too large to be printed".format(self.N))
            return 
        # print dn
        # print(' '*4, end='') 
        for i in range(0,2*self.N):
            print('{: >2d}'.format(self.dp[i]),end='')
        print() 
        for i in range(self.N-1,-1,-1):
            for j in range(self.N):
                if self.bd[j] == i:
                    print(' 1',end='')
                else:
                    print(' 0',end='')
            print()

        for i in range(0,2*self.N):
            print('{: >2d}'.format(self.dn[i]),end='') 
        print()
        if bd:
            print("board is {}".format(self.bd))

        if attack:
            print("attack list is {}".format(self.attack))
            
    def greedyinit(self,):
        np.random.shuffle(self.bd) 
        reached = False 
        self.threshold = 100
        #print("greedy initialization")
        for i in range(self.N):
            if self.with_progressbar_when_initializing:
                update_progress(i/self.N) 
            if not reached:
                if self.dp[self.N-self.bd[i]+i] == 0 and self.dn[self.bd[i]+i+1] == 0:
                    self.dp[self.N-self.bd[i]+i] += 1
                    self.dn[self.bd[i]+i+1] += 1
                else:
                    foundit = False 
                    for j in range(self.threshold):
                        # print("i = {}, self.N = {}".format(i,self.N))
                        tmp = np.random.randint(i,self.N)
                        if self.dp[self.N-tmp+i] == 0 and self.dn[tmp+i+1] == 0:
                            self.bd[i], self.bd[tmp] = self.bd[tmp], self.bd[i]
                            self.dp[self.N-self.bd[i]+i] += 1
                            self.dn[self.bd[i]+i+1] += 1                
                            foundit = True
                            break 
                        if j == self.threshold-1:
                            reached = True
                            break 

                    if not foundit:
                        self.dp[self.N-self.bd[i]+i] += 1
                        self.dn[self.bd[i]+i+1] += 1                    
            else:
                self.dp[self.N-self.bd[i]+i] += 1
                self.dn[self.bd[i]+i+1] += 1

        total = 0
        for i in self.dn:
            if i > 1:
                total += i-1
        for j in self.dp:
            if j > 1:
                total += j-1
        self.collisions = total 
        self.compute_attack_matrix()
        
    def randinit(self,):
        np.random.shuffle(self.bd) 
        self.compute_collisions()
        self.compute_attack_matrix()


    def compute_attack_matrix(self,):
        self.attack = [] 
        for i in range(self.N):
            if self.dp[self.N-self.bd[i]+i] > 1 or self.dn[self.bd[i]+i+1] > 1:
                self.attack.append(i)
        return self.attack 
        
    def compute_collisions(self,):
        self.dp.fill(0)
        self.dn.fill(0)
        for i in range(self.N):
            self.dp[self.N-self.bd[i]+i] += 1
            self.dn[self.bd[i]+i+1] += 1
        total = 0
        for i in self.dn:
            if i > 1:
                total += i-1
        for j in self.dp:
            if j > 1:
                total += j-1
        self.collisions = total 
        return total 
   
    def get8collisions(self,i,j):
        old_collisions = 0
        dpset = [self.N-self.bd[i]+i, self.N-self.bd[i]+j, self.N-self.bd[j]+j,self.N-self.bd[j]+i]
        dpset = list(set(dpset))
        for k in dpset:
            old_collisions += self.dp[k]-1 if self.dp[k] > 1 else 0
        dnset = [self.bd[i]+i+1, self.bd[i]+j+1, self.bd[j]+j+1, self.bd[j]+i+1]
        dnset = list(set(dnset))
        for k in dnset:
            old_collisions += self.dn[k]-1 if self.dn[k] > 1 else 0

        return old_collisions

    def swap_ok(self,i,j):
        self._old = self.get8collisions(i,j)
        self._perform_swap(i,j)
        self._new = self.get8collisions(i,j)
        self._perform_swap(j,i)
        return self._new < self._old

    def _perform_swap(self, i,j):
        self.dp[self.N-self.bd[i]+i] -= 1
        self.dn[self.bd[i]+i+1] -= 1
        self.dp[self.N-self.bd[i]+j] += 1
        self.dn[self.bd[i]+j+1] += 1
        self.dp[self.N-self.bd[j]+j] -= 1
        self.dn[self.bd[j]+j+1] -= 1
        self.dp[self.N-self.bd[j]+i] += 1
        self.dn[self.bd[j]+i+1] += 1
        self.bd[i], self.bd[j] = self.bd[j], self.bd[i] 
    def perform_swap(self, i,j):
        self._perform_swap(i,j)
        self.collisions = self.collisions - self._old + self._new

    def repair(self, withprogressbar=False):
        self.iter_num = 0
        while self.collisions > 0:
            self.iter_num += 1
            self.randinit() 
            self.collisions = self.compute_collisions()
            self.limit = self.collisions * self.C1
            self.loopcount = 0
            #print("\niteration {}".format(self.iter_num))
            while self.loopcount <= self.C2 * self.N:
                if withprogressbar:
                    update_progress(float(self.loopcount) / (self.C2 * self.N))
                for i in self.attack:
                    j = np.random.randint(0,self.N) # choose j
                    if self.swap_ok(i,j):
                        self.perform_swap(i,j) # update collision matrix and board 
                        if self.collisions == 0:
                            return
                        if self.collisions < self.limit:
                            self.limit = self.C1 * self.collisions
                            self.compute_attack_matrix()
                    
                self.loopcount += len(self.attack)
        return True





if __name__ == "__main__":
    board = board(4,randinit=True)
    board.printall(bd=True, attack=True)
    board.repair()
    board.printall(bd=True, attack=True)
    print(board.collisions)
    print("iteration = {}".format(board.iter_num))
