using Test
using MacroAIComp

@testset "Ramsey Tests" begin
    @testset "Ramsey Steady State Calibration" begin
        params = default_calibration(RamseyParams)
        ss = compute_ramsey_steady_state(params)

        @test ss["k"] ≈ 7.9537 atol=1e-4
        @test ss["y"] ≈ 2.0663 atol=1e-4
        @test ss["c"] ≈ 1.4300 atol=1e-4
        @test ss["i"] ≈ 0.6363 atol=1e-4
        @test ss["R"] ≈ 0.0909 atol=1e-4
    end

    @testset "Ramsey Linearized Eigenvalues" begin
        params = default_calibration(RamseyParams)
        _, r_stable, r_unstable, theta = compute_ramsey_transition_matrix(params)

        @test r_stable ≈ -0.0907 atol=1e-4
        @test r_unstable ≈ 0.1115 atol=1e-4
        @test (1.0 + r_stable) ≈ 0.9093 atol=1e-4
        @test (1.0 + r_unstable) ≈ 1.1115 atol=1e-4
        @test theta ≈ 0.5751 atol=1e-4
    end

    @testset "Ramsey TFP Shock Simulation" begin
        params = default_calibration(RamseyParams)
        ss_init = compute_ramsey_steady_state(params)

        T = 100
        t_shock = 5

        # Exogenous paths for non-linear solver
        A_path = fill(1.00, T)
        A_path[(t_shock + 1):end] .= 1.05
        n_path = fill(0.02, T)

        # 1. Solve using linearized stable saddle path
        res_lin = solve_ramsey_linearized(
            params,
            ss_init["k"],
            1.05,
            0.02,
            params.beta,
            T,
            t_shock
        )

        # Capital cannot jump at shock period (index t_shock + 1 = 6 in Julia)
        @test res_lin["k"][t_shock + 1] ≈ ss_init["k"]
        # Deviation at shock period must be on saddle path
        @test res_lin["c_hat"][t_shock + 1] ≈ res_lin["k_hat"][t_shock + 1] * 0.5751 atol=1e-3

        # 2. Solve using non-linear fsolve/nlsolve
        res_nonlin = solve_ramsey_nonlinear(
            params,
            ss_init["k"],
            A_path,
            n_path,
            T,
            t_shock
        )

        # Verify initial and final values match
        params_final = RamseyParams(params.alpha, params.beta, params.delta, 0.02, 1.05)
        ss_final = compute_ramsey_steady_state(params_final)

        # Capital transition is slow
        @test res_nonlin["k"][1] ≈ ss_init["k"]
        @test res_nonlin["k"][end] ≈ ss_final["k"] atol=1e-2
        @test res_nonlin["c"][end] ≈ ss_final["c"] atol=1e-2

        # Compare solvers: they should be very close for a 5% TFP shock
        @test res_lin["k"] ≈ res_nonlin["k"] atol=5e-2 rtol=1e-2
        @test res_lin["c"] ≈ res_nonlin["c"] atol=5e-2 rtol=1e-2
    end
end
