using MacroAIComp

params = default_calibration(RamseyParams)
ss_init = compute_ramsey_steady_state(params)

T = 100
t_shock = 5

# Exogenous paths
A_path = fill(1.00, T)
A_path[(t_shock + 1):end] .= 1.05
n_path = fill(0.02, T)

alpha = params.alpha
beta = params.beta
delta = params.delta
k0 = ss_init["k"]

params_post = RamseyParams(alpha, beta, delta, n_path[end], A_path[end])
ss_post = compute_ramsey_steady_state(params_post)
k_ss_final = ss_post["k"]
c_ss_final = ss_post["c"]

n_post = T - t_shock

function simulate_from_shock(c_shock)
    k_sim = zeros(n_post)
    c_sim = zeros(n_post)
    k_sim[1] = k0
    c_sim[1] = c_shock
    for t in 1:(n_post - 1)
        idx = t + t_shock
        A_t = A_path[min(idx, length(A_path))]
        n_t = n_path[min(idx, length(n_path))]
        A_t1 = A_path[min(idx + 1, length(A_path))]

        y_t = A_t * k_sim[t]^alpha
        k_sim[t + 1] = ((1.0 - delta) * k_sim[t] + y_t - c_sim[t]) / (1.0 + n_t)
        if k_sim[t + 1] <= 0
            k_sim[t + 1] = 1e-8
        end
        mpk_t1 = alpha * A_t1 * k_sim[t + 1]^(alpha - 1.0)
        c_sim[t + 1] = beta * (1.0 + mpk_t1 - delta) * c_sim[t]
    end
    return k_sim, c_sim
end

function residual(c_shock)
    k_sim, _ = simulate_from_shock(c_shock)
    return k_sim[end] - k_ss_final
end

_, _, _, theta = compute_ramsey_transition_matrix(params_post)
c_shock_guess = c_ss_final * exp(theta * log(k0 / k_ss_final))

# Bisection search
a = c_shock_guess * 0.5
b = c_shock_guess * 1.5

while residual(a) < 0.0
    global a *= 0.5
end
while residual(b) > 0.0
    global b *= 1.5
end

for iter in 1:100
    mid = (a + b) / 2.0
    res = residual(mid)
    if abs(b - a) < 1e-15 || abs(res) < 1e-15
        break
    end
    if res > 0.0
        global a = mid
    else
        global b = mid
    end
end
c_shock = (a + b) / 2.0

k_sim, c_sim = simulate_from_shock(c_shock)
println("Converged c_shock: ", c_shock)
println("Final k_sim: ", k_sim[end], " (target: ", k_ss_final, ")")
println("Final c_sim: ", c_sim[end], " (target: ", c_ss_final, ")")
