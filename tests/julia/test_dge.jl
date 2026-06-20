using Test
using LinearAlgebra
using MacroAIComp

@testset "DGE Tests" begin
    @testset "Steady State Calibration" begin
        params = default_calibration(DGEParams)
        ss = compute_steady_state(params)

        @test ss["K"] ≈ 6.698596 atol=1e-6
        @test ss["Y"] ≈ 1.945783 atol=1e-6
        @test ss["C"] ≈ 1.543867 atol=1e-6
        @test ss["I"] ≈ 0.401916 atol=1e-6
        @test ss["R"] ≈ 0.10166666666666667 atol=1e-6
    end

    @testset "Blanchard-Khan Stability" begin
        params = default_calibration(DGEParams)
        
        Omega = 1.0 - params.beta + params.beta * params.delta
        Phi = 1.0 - params.beta + (1.0 - params.alpha) * params.beta * params.delta

        A_static = [1.0 0.0; Omega -params.alpha * params.beta * params.delta]
        B = [0.0 params.alpha; Phi 0.0]
        A_inv = inv(A_static)

        D = [1.0 Omega; 0.0 1.0]
        F = [-Omega 0.0; 0.0 0.0]
        G = [1.0 0.0; 0.0 1.0 - params.delta]
        H = [0.0 0.0; 0.0 params.delta]

        D_tilde = D + F * A_inv * B
        J = inv(D_tilde) * (G + H * A_inv * B)

        eigenvals = sort(abs.(eigen(J).values))
        mu_1, mu_2 = eigenvals[1], eigenvals[2]

        @test mu_1 < 1.0
        @test mu_2 > 1.0

        @test mu_1 ≈ 0.90399 atol=1e-5
        @test mu_2 ≈ 1.15229 atol=1e-5
    end

    @testset "TFP Shock Simulation" begin
        params = default_calibration(DGEParams)
        T = 100

        ss = compute_steady_state(params)
        K0 = ss["K"]

        # Generate TFP shock path: 1.0 at t=1, 1.01 at t=2, decaying with rho=0.8
        a_hat = zeros(T)
        a_hat[1] = 0.0
        a_hat[2] = 0.01
        for t in 3:T
            a_hat[t] = params.rho * a_hat[t - 1]
        end
        A_path = exp.(a_hat)

        # Solve using both solvers
        res_bk = solve_blanchard_khan(params, K0, A_path, T)
        res_nonlin = solve_nonlinear_simulation(params, K0, A_path, T)

        # 1. Predetermined capital stock: K[1] = K_ss in both simulations
        @test res_bk["K"][1] ≈ K0 atol=1e-12
        @test res_nonlin["K"][1] ≈ K0 atol=1e-12

        # 2. Consumption, Output, and Investment jump on impact (t=2, index 2)
        @test res_bk["C"][2] > ss["C"]
        @test res_bk["Y"][2] > ss["Y"]
        @test res_bk["I"][2] > ss["I"]

        @test res_nonlin["C"][2] > ss["C"]
        @test res_nonlin["Y"][2] > ss["Y"]
        @test res_nonlin["I"][2] > ss["I"]

        # 3. Capital stock peaks with delay (hump-shape)
        # Capital at index 2 (period 2) is predetermined by period 1 (steady state).
        # Capital at index 3 (period 3) should be higher than steady state.
        @test res_bk["K"][3] > K0
        @test res_nonlin["K"][3] > K0

        # Peak in capital should occur in the first few periods (e.g. index 3 to 13)
        bk_k_peak_idx = argmax(res_bk["K"])
        nonlin_k_peak_idx = argmax(res_nonlin["K"])
        @test 3 <= bk_k_peak_idx <= 13
        @test 3 <= nonlin_k_peak_idx <= 13

        # 4. Long run convergence back to initial steady state
        @test res_bk["C"][end] ≈ ss["C"] atol=1e-3
        @test res_bk["K"][end] ≈ K0 atol=1e-3
        @test res_nonlin["C"][end] ≈ ss["C"] atol=1e-3
        @test res_nonlin["K"][end] ≈ K0 atol=1e-3

        # 5. Consistency check: Blanchard-Khan and non-linear simulation must be very close
        @test res_bk["K"] ≈ res_nonlin["K"] rtol=1e-2
        @test res_bk["C"] ≈ res_nonlin["C"] rtol=1e-2
    end
end
