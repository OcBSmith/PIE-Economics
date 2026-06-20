using Optim
using NLsolve

# Define parameters
T = 30
beta = 0.97
R = 0.02
gamma = 0.5
B0 = 0.0
W = fill(30.0, T)
growth = beta * (1.0 + R)

function log_barrier(u, epsilon=1e-9)
    if u > epsilon
        return log(u)
    else
        return log(epsilon) - (epsilon - u) / epsilon - 0.5 * ((epsilon - u) / epsilon)^2
    end
end

# FOC solver
function solve_foc()
    function build_path(C0)
        C = [C0 * (growth^t) for t in 0:(T - 1)]
        L = clamp.(1.0 .- (1.0 - gamma) .* C ./ (gamma .* W), 0.0, 1.0 - 1e-9)
        B = zeros(T)
        B[1] = (1.0 + R) * B0 + W[1] * L[1] - C[1]
        for t in 2:T
            B[t] = (1.0 + R) * B[t - 1] + W[t] * L[t] - C[t]
        end
        return C, L, B
    end

    function residuals!(F, x)
        C0 = x[1]
        _, _, B = build_path(C0)
        F[1] = B[T]
    end

    C0_guess = [(sum(W) / T) * gamma]
    sol = nlsolve(residuals!, C0_guess, xtol=1e-12, ftol=1e-12)
    C, L, B = build_path(sol.zero[1])
    return C, L, B
end

# Direct optimizer with C2 log barrier
function solve_optim()
    function objective(x)
        B = [x..., 0.0]
        C = zeros(T)
        L = zeros(T)

        C[1] = gamma * ((1.0 + R) * B0 + W[1] - B[1])
        L[1] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B0 + W[1] - B[1]) / W[1]
        for t in 2:T
            C[t] = gamma * ((1.0 + R) * B[t - 1] + W[t] - B[t])
            L[t] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B[t - 1] + W[t] - B[t]) / W[t]
        end

        val = 0.0
        for t in 1:T
            val += beta^(t - 1) * (gamma * log_barrier(C[t], 1e-9) + (1.0 - gamma) * log_barrier(1.0 - L[t], 1e-9))
        end
        return -val
    end

    L_const = 0.5
    C_const = (sum(W) / T) * L_const * gamma
    B_guess = zeros(T - 1)
    B_guess[1] = (1.0 + R) * B0 + W[1] * L_const - C_const
    for t in 2:(T - 1)
        B_guess[t] = (1.0 + R) * B_guess[t - 1] + W[t] * L_const - C_const
    end

    res = optimize(objective, B_guess, BFGS(), Optim.Options(g_tol=1e-12, iterations=2000))
    best_B = res.minimizer

    B = [best_B..., 0.0]
    C = zeros(T)
    L = zeros(T)
    C[1] = gamma * ((1.0 + R) * B0 + W[1] - B[1])
    L[1] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B0 + W[1] - B[1]) / W[1]
    for t in 2:T
        C[t] = gamma * ((1.0 + R) * B[t - 1] + W[t] - B[t])
        L[t] = 1.0 - (1.0 - gamma) * ((1.0 + R) * B[t - 1] + W[t] - B[t]) / W[t]
    end
    return C, L, B
end

C_f, L_f, B_f = solve_foc()
C_o, L_o, B_o = solve_optim()

println("Max diff C: ", maximum(abs.(C_f .- C_o)))
println("Max diff L: ", maximum(abs.(L_f .- L_o)))
println("Max diff B: ", maximum(abs.(B_f .- B_o)))
