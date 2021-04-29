import sys
import numpy as np 
import math
import BP_config

nb_trials = 1
print('nb_trials:', nb_trials)

nb_qubits = 3600
print('nb of qubits :', nb_qubits)

Hx_as_rows = np.load('Hx_as_rows_' + str(nb_qubits) + '.npy')
Hx_as_columns = np.load('Hx_as_columns_' + str(nb_qubits) + '.npy')
logicals_basis = np.load('X_logicals_' + str(nb_qubits) + '.npy')

nb_qubits = len(Hx_as_columns)
nb_checks = len(Hx_as_rows)
# print('nb_checks:', nb_checks)

qubit_to_check_degree = len(Hx_as_columns[0])
check_to_qubit_degree = len(Hx_as_rows[0])

nb_BP_rounds = 10

# physical_error_rate = 0.05
# print('physical_error_rate: ', physical_error_rate,'\n')
# initial_error = np.random.binomial(1,physical_error_rate,nb_qubits)

def log_ratio(p):
        return math.log((1-p)/p)

def message_from_check_to_qubit(check_is_on, llr_list):
        
        # llr_list has length 11 (or 12 if noisy syndrome) and corresponds to log ratios of the error likelihoods (for themselves) of the eleven other qubits.

        th_llr_over_2 = 1
        for l in llr_list:
                th_llr_over_2 *= math.tanh(l/2)

        eps = 0.0000000000000001
        if th_llr_over_2==1: th_llr_over_2 -= eps
        if th_llr_over_2==-1: th_llr_over_2 += eps
        llr = 2*math.atanh(th_llr_over_2)

        if check_is_on==0: return llr
        elif check_is_on==1: return -llr
        else: print('ERROR: wrong value for check is on') 

def message_from_qubit_to_check(physical_error_rate, llr_list):

        # llr_list has length 4 (or 5) and kind of corresponds to log ratios of the error likelihoods (for this qubit) coming from the four other (or five) input checks.       

        llr = log_ratio(physical_error_rate) + sum(llr_list)
        return llr

def compute_syndrome(qubit_error):

        syndrome = []
        for c in range(nb_checks):
                s = 0
                for q in Hx_as_rows[c]:
                        s += qubit_error[q]
                syndrome.append(s%2)

        return np.array(syndrome)

def weight(syndrome):
        result=0
        for s in syndrome:
                result+=s
        return result

def check_neighbour_index(qubit, check):

        counter = 0
        for adjacent_check in Hx_as_columns[qubit]:
                if adjacent_check==check:
                        return counter
                counter+=1
        print('check index not found')
        return -1

def qubit_neighbour_index(check, qubit):

        counter = 0
        for adjacent_qubit in Hx_as_rows[check]:
                if adjacent_qubit==qubit:
                        return counter
                counter+=1
        print('qubit index not found')
        return -1


def BP(syndrome, physical_error_rate, noisy_syndrome):

        llr = log_ratio(physical_error_rate)

        qubit_to_check_belief_as_rows = llr * np.ones_like(Hx_as_rows, dtype=float)                             
        check_to_qubit_belief_as_columns = np.zeros_like(Hx_as_columns, dtype=float) # any value would work

        old_inferred_error = np.array([0 for check in range(nb_qubits)])
        new_inferred_error = np.array([0 for check in range(nb_qubits)])

        new_residual_syndrome = syndrome

        w_old_residual_syndrome = nb_qubits
        w_new_residual_syndrome = weight(new_residual_syndrome)


        for _ in range (nb_BP_rounds):

                # half-round : messages from checks to qubits
                for check in range(nb_checks):

                        for first_neighbour_index in range(check_to_qubit_degree):
                                llr_list = []

                                for second_neighbour_index in range(check_to_qubit_degree):
                                        if first_neighbour_index!=second_neighbour_index:
                                                llr_list.append(qubit_to_check_belief_as_rows[check,second_neighbour_index])

                                if noisy_syndrome: llr_list.append(log_ratio(physical_error_rate))

                                qubit = Hx_as_rows[check,first_neighbour_index]
                                check_to_qubit_belief_as_columns[qubit,check_neighbour_index(qubit,check)] = message_from_check_to_qubit(syndrome[check],llr_list)

                # half-round : messages from qubits to checks
                for qubit in range(nb_qubits):

                        for first_neighbour_index in range(qubit_to_check_degree):
                                llr_list = []

                                for second_neighbour_index in range(qubit_to_check_degree):
                                        if first_neighbour_index!=second_neighbour_index:
                                                llr_list.append(check_to_qubit_belief_as_columns[qubit,second_neighbour_index])

                                check = Hx_as_columns[qubit,first_neighbour_index]
                                qubit_to_check_belief_as_rows[check,qubit_neighbour_index(check,qubit)] = message_from_qubit_to_check(physical_error_rate,llr_list)

                # compute syndromes if we were to stop here
                final_llr_list = []
                old_inferred_error = new_inferred_error
                new_inferred_error = []
                w_old_residual_syndrome = w_new_residual_syndrome

                for qubit in range(nb_qubits):
                        llr_list = []

                        for neighbour_index in range(qubit_to_check_degree):
                                llr_list.append(check_to_qubit_belief_as_columns[qubit,neighbour_index])
                        
                        final_llr_list.append( message_from_qubit_to_check(physical_error_rate,llr_list) )

                        if (final_llr_list[qubit]<0): new_inferred_error.append(1)
                        else: new_inferred_error.append(0)

                new_inferred_syndrome = compute_syndrome(new_inferred_error)
                new_residual_syndrome = np.add(syndrome,new_inferred_syndrome)%2
                w_new_residual_syndrome = weight(new_residual_syndrome)

                # print('weight old synd:',w_old_residual_syndrome,'weight new synd:',w_new_residual_syndrome)

        return np.array(old_inferred_error)


def is_in_the_image(residual_error,logicals_basis):
        if np.any(np.mod(np.dot(logicals_basis,residual_error),2)):
            return 0
        else:
            return 1


def noisy_decoder(error,physical_error_rate,T=1):

        # print('T=',T) 

        new_error = np.random.binomial(1,physical_error_rate,nb_qubits)
        error = np.add(error,new_error)%2
        syndrome = compute_syndrome(error)
        flag_noisy_syndrome = 0
        
        if T>1:
                syndrome_noise = np.random.binomial(1,physical_error_rate,nb_checks)
                syndrome = np.add(syndrome,syndrome_noise)%2
                flag_noisy_syndrome = 1

        inferred_error = BP(syndrome, physical_error_rate, flag_noisy_syndrome)
        error = np.add(error,inferred_error)%2

        if T>1:
                return noisy_decoder(error,physical_error_rate,T-1)

        elif T==1:
                syndrome = compute_syndrome(error)
                if not weight(syndrome)==0:
                        return 'decoding did not terminate'
                else:
                        if is_in_the_image(error,logicals_basis): return 'successful decoding'
                        else: return 'logical error'


        else: print('wrong value for T')


def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step


# physical_error_rate = 1.5*10**(-1)
# physical_error_rate = 7*10**(-2)
# physical_error_rate = 4*10**(-2)
# physical_error_rate = 3*10**(-2)
# physical_error_rate = 1.5*10**(-2)
# physical_error_rate = 7*10**(-3)
# physical_error_rate = 3*10**(-3)
# physical_error_rate = 1.5*10**(-3)
# physical_error_rate = 7*10**(-4)
# physical_error_rate = 3*10**(-4)
# physical_error_rate = 1.5*10**(-4)

# physical_error_rate = 2*10**(-1)
# physical_error_rate = 1*10**(-1)
# physical_error_rate = 5*10**(-2)
# physical_error_rate = 2*10**(-2)
physical_error_rate = 1*10**(-2)
# physical_error_rate = 5*10**(-3)
# physical_error_rate = 2*10**(-3)
# physical_error_rate = 1*10**(-3)
# physical_error_rate = 5*10**(-4)
# physical_error_rate = 2*10**(-4)
# physical_error_rate = 10**(-4)

print('physical_error_rate : ', physical_error_rate)
nb_successful_decoding = 0
nb_logical_error = 0
nb_decoding_did_not_terminate = 0
for trial in range(nb_trials):
        # print('trial nb:',trial)
        initial_error = np.array([0 for qubit in range(nb_qubits)])
        decoding_result = noisy_decoder(initial_error,physical_error_rate)
        if decoding_result=='logical error': nb_logical_error += 1
        if decoding_result=='decoding did not terminate': nb_decoding_did_not_terminate += 1
        # if trial%(int(nb_trials/100))==0 : print(int(100*trial/nb_trials + 0.0001), '/ 100')

idx = sys.argv[1]
# print('idx:', idx)
output_file = BP_config._OUTPUT_BASE_NAME + '{}.txt'.format(idx)
nb_failed_decoding = nb_logical_error + nb_decoding_did_not_terminate
result = [physical_error_rate, nb_trials, nb_logical_error, nb_decoding_did_not_terminate, nb_failed_decoding]
with open(output_file, 'w') as f:
        for x in result:
                f.write(str(x) + '\n')


# print('physical_error_rate : ', physical_error_rate)
print('nb_failed_decoding =', nb_failed_decoding)











